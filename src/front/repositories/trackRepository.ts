import { API_BASE_URL } from "@config/index";
import { AlertManager } from "@utils/alertManager";

export class TrackRepository {
  async getByUrl(url: string) {
    const response = await fetch(`${API_BASE_URL}/tracks/by-url?url=${encodeURIComponent(url)}`);
    if (!response.ok) {
      throw new Error("Track not found");
    }
    return response.json();
  }

  async create(playlistId: number, url: string, title: string) {
    try {
      const response = await fetch(`${API_BASE_URL}/playlists/${playlistId}/tracks/by-url`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url, title: title }),
      });

      if (!response.ok) {
        throw new Error("Failed to add track by URL");
      }
      return response.json();
    } catch (err) {
      new AlertManager().error("Failed to add track");
    }
  }

  async delete(playlistId: number, trackId: number) {
    try {
      const response = await fetch(
        `${API_BASE_URL}/playlists/${playlistId}/track/${trackId}`,
        {
          method: "DELETE",
        },
      );

      if (!response.ok) {
        console.log("error from playlist removal")
        throw new Error("Failed to remove track from playlist");
      }
      return response.json();
    } catch (err){
      throw err
    }
  }
}
