from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class AuthorVerification(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author_verifications',
        verbose_name='User',
    )
    book = models.ForeignKey(
        'Book',
        on_delete=models.CASCADE,
        related_name='author_verifications',
    )
    proof_document = models.FileField(
        upload_to='author_proofs/',
        verbose_name='Identity document',
        help_text='PDF or image',
    )
    proof_authorship = models.FileField(
        upload_to='author_proofs/',
        verbose_name='Authorship proof',
        help_text='Publisher contract, book page, etc.',
    )
    publisher_url = models.URLField(blank=True, verbose_name='Official publisher page')
    additional_notes = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        db_index=True,
    )
    admin_note = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_verifications',
    )

    class Meta:
        verbose_name = 'Author verification'
        verbose_name_plural = 'Author verifications'
        ordering = ['-submitted_at']

    def __str__(self):
        return f'{self.user.username} → {self.book.title} ({self.get_status_display()})'

    def approve(self, admin_user, note=''):
        from core.notifications import notify_author_approved

        self.status = self.STATUS_APPROVED
        self.admin_note = note
        self.reviewed_at = timezone.now()
        self.reviewed_by = admin_user
        self.save()

        self.book.verified_author = self.user
        self.book.save(update_fields=['verified_author'])

        self.user.profile.is_verified_author = True
        self.user.profile.save(update_fields=['is_verified_author'])

        notify_author_approved(self)

    def reject(self, admin_user, note=''):
        from core.notifications import notify_author_rejected

        self.status = self.STATUS_REJECTED
        self.admin_note = note
        self.reviewed_at = timezone.now()
        self.reviewed_by = admin_user
        self.save()

        notify_author_rejected(self)
