const Player = (() => {
    const EMBED_BUILDERS = {
        youtube: (code) =>
            `https://www.youtube.com/embed/${code}?autoplay=1&rel=0`,
        spotify: (code) =>
            `https://open.spotify.com/embed/track/${code}?autoplay=1`,
        soundcloud: (code) =>
            `https://w.soundcloud.com/player/?url=${encodeURIComponent(code)}&auto_play=true&color=%23c4622d`,
        other: null,
    };

    let currentTrackId = null;

    const bar = document.getElementById('sticky-player');
    const iframe = document.getElementById('player-iframe');
    const titleEl = document.getElementById('player-title');
    const artistEl = document.getElementById('player-artist');
    const closeBtn = document.getElementById('player-close');

    function buildEmbedUrl(linkType, embedCode, linkUrl) {
        const builder = EMBED_BUILDERS[linkType];
        if (!builder) return null;

        const source = (linkType === 'soundcloud') ? linkUrl : embedCode;
        if (!source) return null;

        return builder(source);
    }

    function load(trackId, title, artist, linkType, embedCode, linkUrl) {
        if (currentTrackId === trackId) {
            toggle();
            return;
        }

        const url = buildEmbedUrl(linkType, embedCode, linkUrl);

        if (!url) {
            window.open(linkUrl, '_blank', 'noopener,noreferrer');
            return;
        }

        currentTrackId = trackId;

        iframe.src = url;
        titleEl.textContent = title;
        artistEl.textContent = artist;

        bar.classList.remove('player--hidden');
        bar.classList.add('player--visible');

        updateActiveButton(trackId);
    }

    function toggle() {
        const isHidden = bar.classList.contains('player--hidden');
        bar.classList.toggle('player--hidden', !isHidden);
        bar.classList.toggle('player--visible', isHidden);
    }

    function close() {
        iframe.src = '';
        currentTrackId = null;
        bar.classList.remove('player--visible');
        bar.classList.add('player--hidden');
        clearActiveButtons();
    }

    function updateActiveButton(trackId) {
        clearActiveButtons();
        const btn = document.querySelector(`.play-btn[data-track-id="${trackId}"]`);
        if (btn) btn.classList.add('play-btn--active');
    }

    function clearActiveButtons() {
        document.querySelectorAll('.play-btn--active').forEach(el => {
            el.classList.remove('play-btn--active');
        });
    }

    function init() {
        if (!bar) return;

        closeBtn?.addEventListener('click', close);

        document.querySelectorAll('.play-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                load(
                    btn.dataset.trackId,
                    btn.dataset.title,
                    btn.dataset.artist,
                    btn.dataset.linkType,
                    btn.dataset.embedCode,
                    btn.dataset.linkUrl,
                );
            });
        });
    }

    return {init};
})();

document.addEventListener('DOMContentLoaded', Player.init);