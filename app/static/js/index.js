function setLoadingState(isLoading) {
    const button = document.getElementById('search-btn');
    const loadingIndicator = document.getElementById('loadingIndicator');
    if (isLoading) {
        button.disabled = true;
        loadingIndicator.style.display = 'block';
    } else {
        button.disabled = false;
        loadingIndicator.style.display = 'none';
    }
}

async function processSearch(url_input) {
    setLoadingState(true);
    const { resource, data } = await displayResource(url_input);

    let newTitle;
    if (data && data.name) {
        newTitle = `${data.name} | Music Manager`;
    } else {
        newTitle = 'Music Manager';
        history.pushState({ url: data.url }, newTitle, `#${encodeURIComponent(data.url)}`);
        document.title = newTitle;
        updateButton();
    }
    setLoadingState(false);
}

async function downloadResource(url) {
    setLoadingState(true);
    try {
        const response = await fetch(`/download/?url=${url}`, { method: "GET" });
        const data = await response.json();
        if (response.ok) {
            return display(data);
        } else {
            console.error("Failed to fetch the resource");
        }
    } catch (error) {
        console.error("An error occurred:", error);
    } finally {
        setLoadingState(false);
    }
}

async function displayResource(url) {
    setLoadingState(true);
    try {
        const response = await fetch(`/query/?url=${url}`, { method: "GET" });
        const data = await response.json();
        if (response.ok) {
            
            return display(data);
        } else {
            console.error("Failed to fetch the resource");
        }
    } catch (error) {
        console.error("An error occurred:", error);
    } finally {
        setLoadingState(false);
    }
}

function display(responseContent) {
    if (!history.state || history.state.url !== responseContent.data[0].url) {
        const newTitle = `${responseContent.data[0].name} | Music App`;
        history.pushState({ url: responseContent.data[0].url }, newTitle, `#${encodeURIComponent(responseContent.data[0].url)}`);
        document.title = newTitle;
    }
    const albumInfoContainer =
        document.getElementById("albumInfoContainer");
    const { resource, data } = responseContent;
    const url = data[0].url;
    document.getElementById("spotifyUrl").value = url;
    let html = "";
    const img = (src, alt) =>
        `<img src="${src}" alt="${alt}" class="mx-auto max-h-[25dvh] portrait:max-h-[10dvh] portrait:sm:max-h-[16dvh] ">`;
    const title = (text) =>
        `<h1 class="text-white text-3xl font-bold landscape:6xl">${text}</h1>`;
    switch (resource) {
        case "artist":
            const artist = data[0];
            html = `
        ${img(artist.images[0].url, artist.name)}
        ${title(artist.name)}
        <p class="text-gray-500">${artist.tracks
                } songs, ${formatTotalDuration(artist.total_duration)}</p>
        `;
            break;
        case "album":
            const album = data[0];
            html = `
          ${img(
                album.images[0].url,
                album.artists.map((a) => a.name).join(", ") + " - " + album.name
            )}
            ${title(album.name)}
            <p>By ${album.artists
                    .map((artist) =>
                        generateQueryClick(artist.name, "artist", artist.id)
                    )
                    .join(", ")}</p>
            <p class="text-gray-500">${formatDuration(
                        album.release_date
                    )} · ${album.tracks} songs, ${formatTotalDuration(
                        album.total_duration
                    )}</p>
            `;
            break;
        case "playlist":
            const playlist = data[0];
            html = `
              ${img(
                playlist.images[0].url,
                `Playlist cover - ${playlist.author_name} ${playlist.name}`
            )}
              ${title(playlist.name)}
              <p class="text-neutral-300">by ${playlist.author_name}</p>
              <p class="text-gray-500">${playlist.tracks
                } songs, ${formatTotalDuration(playlist.total_duration)}</p>
              `;
            break;
        case "track":
            return displayResource(
                `https://open.spotify.com/album/${data["album_id"]}`
            );
        default:
            break;
    }
    albumInfoContainer.innerHTML = html;
    const tracksContainer = document.getElementById("tracksContainer");
    const tracksContainerHeader = document.getElementById(
        "tracksContainerHeader"
    );
    const clockIcon = `<svg xmlns="http://www.w3.org/2000/svg" fill="white" width="20" height="20" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm1-13h-2v6l5.25 3.15.75-1.23-4.5-2.67V7z"/></svg>`;
    const tracksContainerHeaderHtml = `
      <div class="col-span-1 h-8 py-1  text-center">#</div>
      <div class="col-span-1 h-8 py-1 px-1  text-center">Year</div>
      <div class="col-span-3 h-8 py-1 px-1 ">Track</div>
      <div class="col-span-2 h-8 py-1 px-1  text-left">Album</div>
      <div class="col-span-2 h-8 py-1 px-1 text-left">Artist</div>
      <div class="flex items-center justify-center w-full col-span-1 h-8 py-1 px-1  text-center">${clockIcon}</div>
    `;
    const tracksContainerHtml = data[1]
        .map((track, i) => {
            const rowClass = i % 2 === 0 ? "bg-white bg-opacity-10" : "";
            const trackNumber = `<div class="col-span-1 h-8 py-1 text-center truncate ${rowClass}">${i + 1
                }</div>`;
            const year = `<div class="col-span-1 py-1 px-1 text-center truncate h-8 ${rowClass}">${track.year}</div>`;
            const name = `<div class="col-span-3 h-8 py-1 px-1 truncate ${rowClass}">${track.name}</div>`;
            const album = `<div class="col-span-2 h-8 py-1 px-1 text-left truncate ${rowClass}">${generateQueryClick(
                track.album_name,
                "album",
                track.album_id
            )}</div>`;
            const artist = `<div class="col-span-2 h-8 py-1 px-1 text-left truncate ${rowClass}">${track.artists.join(
                ", "
            )}</div>`;
            const duration = `<div class="col-span-1 h-8 py-1 px-1 text-center truncate ${rowClass}">${formatTime(
                track.duration
            )}</div>`;
            return trackNumber + year + name + album + artist + duration;
        })
        .join("");
    tracksContainerHeader.innerHTML = tracksContainerHeaderHtml;
    tracksContainer.innerHTML = tracksContainerHtml;
    return data;
}

function updateButton() {
    const urlInput = document.getElementById("spotifyUrl").value;
    const resourceType = getResourceType(urlInput);
    const button = document.getElementById("search-btn");
    if (resourceType) {
        button.textContent = `Search ${resourceType[0].toUpperCase()}${resourceType.slice(
            1
        )}`;
    } else {
        button.textContent = "Enter link";
    }
}

function generateQueryClick(name, resource, id) {
    return `<span onclick="queryClicked('${resource}', '${id}')" class="cursor-pointer">${name}</span>`;
}

function queryClicked(resource, id) {
    const url = `https://open.spotify.com/${resource}/${id}`;
    document.getElementById("spotifyUrl").value = url;
    console.log("Query clicked:", resource, id);
    displayResource(url);
    updateButton();
}

function getResourceType(url) {
    const regex =
        /https:\/\/open.spotify.com\/(artist|track|playlist|album)\/([a-zA-Z0-9]+)/;
    const match = url.match(regex);
    return match ? match[1] : null;
}

function formatTime(seconds) {
    const minutes = Math.floor(seconds / 60);
    const sec = seconds % 60;
    return `${minutes}:${sec < 10 ? "0" + sec : sec}`;
}

function formatTotalDuration(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    const hourLabel = hours === 1 ? "hour" : "hours";

    return `${hours} ${hourLabel} ${minutes} min ${secs} sec`;
}

function formatDuration(dateStr) {
    const months = [
        "Jan.",
        "Feb.",
        "Mar.",
        "Apr.",
        "May",
        "Jun.",
        "Jul.",
        "Aug.",
        "Sep.",
        "Oct.",
        "Nov.",
        "Dec.",
    ];
    const date = new Date(dateStr);
    return `${String(date.getDate()).padStart(2, "0")} ${months[date.getMonth()]
        } ${date.getFullYear()}`;
}

document
    .getElementById("albumForm")
    .addEventListener("submit", async (event) => {
        event.preventDefault();
        const url = document.getElementById("spotifyUrl").value;
        await downloadResource(url);
        updateButton();
    });

document
    .getElementById("search-btn")
    .addEventListener("click", async () => {
        const url = document.getElementById("spotifyUrl").value;
        await processSearch(url);
        updateButton();
    });

window.onpopstate = function (event) {
    setLoadingState(false);
    const spotifyUrlInput = document.getElementById("spotifyUrl");
    if (event.state && event.state.url) {
        spotifyUrlInput.value = event.state.url;
        displayResource(event.state.url);
    } else {
        const initialUrl = spotifyUrlInput.value;
        if (initialUrl) displayResource(initialUrl);
    }
    updateButton();
};

window.addEventListener("load", function () {
    setLoadingState(false);
    const hash = window.location.hash.substr(1);
    if (hash) {
        const decodedUrl = decodeURIComponent(hash);
        document.getElementById("spotifyUrl").value = decodedUrl;
        displayResource(decodedUrl);
    }
    updateButton();
});
