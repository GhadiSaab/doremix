import YoutubePlayer from '@store/trackPlayer';
import playlist1 from '@assets/images/playlist1.jpg';
import playIcon from '@assets/icons/play.svg';
import pauseIcon from '@assets/icons/pause.svg';
import { routerInstance } from '../../main';

let currentTrackIndex = 0;
let overlayTrackRows: HTMLElement[] = [];

const highlightOverlayTrack = (index: number) => {
  overlayTrackRows.forEach((row, idx) => {
    row.classList.toggle('bg-white/10', idx === index);
    row.classList.toggle('border-l-2', idx === index);
    row.classList.toggle('border-primary', idx === index);
  });
};

const openOverlay = (container: HTMLElement) => {
  const overlay = container.querySelector('#playlistOverlay');
  if (overlay) {
    overlay.classList.remove('hidden');
    document.body.classList.add('overflow-hidden');
  }
};

const updateNowPlayingMeta = (container: HTMLElement, playerStore: YoutubePlayer) => {
  if (!playerStore) return;

  const cover = container.querySelector('#playerCover') as HTMLImageElement;
  const title = container.querySelector('#currentTrack') as HTMLElement;
  const playlistName = container.querySelector('#currentPlaylistName') as HTMLElement;
  const playlist = playerStore.playlist;

  if (cover && playlist) {
    cover.src = playlist.image || cover.src;
  }
  if (playlistName && playlist) {
    playlistName.textContent = playlist.name || '';
  }
  if (title && playlist) {
    const track = playlist.tracks[currentTrackIndex || 0];
    title.textContent = track?.title || title.textContent;
  }
};

const setupControlButtons = (container: HTMLElement, playerStore: YoutubePlayer) => {
  const playBtn = container.querySelector('#playBtn');
  const pauseBtn = container.querySelector('#pauseBtn');
  const previousBtn = container.querySelector('#previousBtn');
  const nextBtn = container.querySelector('#nextBtn');
  const trackTimer = container.querySelector('#trackTimer');
  const playlistInfo = container.querySelector('#playerContainer .playlist-info');

  if (!playBtn || !trackTimer) {
    throw new Error('Some buttons were not found');
  }

  playBtn.addEventListener('click', () => {
    playerStore?.changeTrackState();
  });

  pauseBtn.addEventListener('click', () => {
    playerStore?.changeTrackState();
  });

  if (previousBtn) {
    previousBtn.addEventListener('click', () => {
      playerStore?.previousTrack();
    });
  }

  if (nextBtn) {
    nextBtn.addEventListener('click', () => {
      playerStore?.nextTrack();
    });
  }

  let isSeeking = false;

  trackTimer.addEventListener('mousedown', () => {
    isSeeking = true;
    playerStore?.stopTimer();
  });

  trackTimer.addEventListener('input', (event: Event) => {
    if (!isSeeking) return;
    const target = event.target as HTMLInputElement;
    if (!target) return;

    const elapsedTime = container.querySelector('#trackElapsedTime') as HTMLElement;
    if (elapsedTime) {
      elapsedTime.textContent = new Date(Number(target.value) * 1000).toISOString().substr(14, 5);
    }

    // Update CSS variable for Chrome progress styling
    const progress = (parseFloat(target.value) / parseFloat(target.max)) * 100;
    target.style.setProperty('--range-progress', `${progress}%`);
  });

  trackTimer.addEventListener('mouseup', (event: Event) => {
    if (!isSeeking) return;
    const target = event.target as HTMLInputElement;
    if (!target) return;

    playerStore?.setTrackTime(Number(target.value));
    isSeeking = false;

    // Wait a bit for the seek to complete before restarting the timer
    setTimeout(() => {
      playerStore?.setTimer();
    }, 100);
  });

  // Handle case where user drags outside and releases
  trackTimer.addEventListener('mouseleave', (event: Event) => {
    if (!isSeeking) return;
    const target = event.target as HTMLInputElement;
    if (!target) return;

    playerStore?.setTrackTime(Number(target.value));
    isSeeking = false;
    setTimeout(() => {
      playerStore?.setTimer();
    }, 100);
  });

  if (playlistInfo && routerInstance) {
    routerInstance.navigate("Router");
    playlistInfo.addEventListener('click', () => {
      openOverlay(container);
    });
  }
};

const initializePlayer = (container: HTMLElement, playerStore: YoutubePlayer) => {
  setupControlButtons(container, playerStore);

  const originalPlayTrack = playerStore.playTrack.bind(playerStore);
  playerStore.playTrack = (index: number = 0) => {
    originalPlayTrack(index);
    currentTrackIndex = index;
    highlightOverlayTrack(index);
    updateNowPlayingMeta(container, playerStore);
  };

  const originalSetPlaylist = playerStore.setPlaylist.bind(playerStore);
  playerStore.setPlaylist = (playlist) => {
    originalSetPlaylist(playlist);
    currentTrackIndex = 0;
    updateNowPlayingMeta(container, playerStore);
  };

  updateNowPlayingMeta(container, playerStore);

  // Load YouTube API
  if (window.YT && window.YT.Player) {
    // API already loaded
  } else {
    const tag = document.createElement('script');
    tag.src = 'https://www.youtube.com/iframe_api';
    const firstScriptTag = document.getElementsByTagName('script')[0];
    firstScriptTag.parentNode?.insertBefore(tag, firstScriptTag);
    (window as any).onYouTubeIframeAPIReady = () => {
      // Player ready
    };
  }
};


export function TrackPlayer() {
  return (
    <div
      class="track-player-container"
    >
      {/* Player controls */}
      <div
        class="fixed bottom-0 left-0 right-0 bg-neutral-900 border-t border-border shadow-2xl backdrop-blur-sm flex items-start md:items-center justify-between md:flex-row flex-col px-6 py-4 hidden"
        id="playerContainer"
      >
        <div
          class="flex items-center justify-between w-full md:w-[420px] gap-4 cursor-pointer playlist-info"
        >
          <img
            id="playerCover"
            src={playlist1}
            class="w-[75px] h-[75px] mr-2 rounded-md hidden md:block object-cover"
            alt="Playlist Cover"
          />
          <div class="flex-1 min-w-0 w-full">
            <div class="now-playing text-xs font-semibold text-primary uppercase tracking-wider mb-1">
              Now Playing
            </div>
            <div
              class="current-track text-lg font-bold text-white truncate text-ellipsis hover:underline"
              id="currentTrack"
            >
              No track selected
            </div>
            <div class="text-sm text-muted-foreground truncate" id="currentPlaylistName"></div>
          </div>
        </div>

        {/* Control buttons */}
        <div class="flex md:flex-col items-center gap-3 w-[520px] max-w-full">
          <div class="flex gap-10 md:order-1 order-2">
            <div class="flex items-center justify-center gap-3">
              <button
                class="control-btn w-10 h-10 rounded-full md:flex items-center justify-center font-bold text-sm shadow-lg hover:shadow-xl hidden"
                id="previousBtn"
                title="Previous Track"
              >
                &lt;&lt;
              </button>

              <button
                class="control-btn w-12 h-12 rounded-full relative flex items-center justify-center font-bold shadow-lg hover:shadow-xl"
                id="playBtn"
                title="Play"
              >
                <img
                  src={playIcon}
                  class="absolute z-99 w-10 p-2 rounded-[999px] cursor-pointer"
                  alt="Play"
                />
              </button>


              <button
                class="control-btn w-12 h-12 rounded-full relative flex items-center justify-center font-bold shadow-lg hover:shadow-xl hidden"
                id="pauseBtn"
                title="Pause"
              >
                <img
                  src={pauseIcon}
                  class="absolute z-99 w-10 p-2 rounded-[999px] cursor-pointer"
                  alt="Pause"
                />
              </button>

              <button
                class="control-btn w-10 h-10 rounded-full md:flex hidden items-center justify-center font-bold text-sm shadow-lg hover:shadow-xl"
                id="nextBtn"
                title="Next Track"
              >
                &gt;&gt;
              </button>
            </div>
          </div>

          {/* Progress bar */}
          <div class="mb-4 w-full flex items-center gap-4">
            <span id="trackElapsedTime" class="hidden md:block"></span>
            <input
              type="range"
              id="trackTimer"
              class="range-input w-full h-1.5"
              min="0"
              max="0"
            />
            <span id="trackTotalTime" class="hidden md:block"></span>
          </div>
        </div>
        <div class="hidden xl:block w-[400px]"></div>
      </div>

      {/* Overlay */}
      <div id="playlistOverlay" class="fixed inset-0 z-40 hidden">
        <div class="absolute inset-0 bg-black/70 backdrop-blur-sm"></div>
      </div>
    </div>
  );
}

// Export initialization function for use in script tags
export { initializePlayer, setupControlButtons };
