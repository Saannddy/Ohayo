import { useState, useCallback } from "react";
import { invoke } from "@tauri-apps/api/core";
import { useAppStore } from "../store/appStore";
import type { Profile } from "../types";

export function useProfiles() {
  const [profiles, setProfiles] = useState<[string, Profile][]>([]);
  const store = useAppStore();

  const loadProfiles = useCallback(async () => {
    try {
      const data = await invoke<[string, Profile][]>("get_profiles");
      setProfiles(data);
    } catch {
      /* ignore */
    }
  }, []);

  const saveProfile = useCallback(async (name: string) => {
    const s = useAppStore.getState();
    const profile: Profile = {
      url: s.url,
      method: s.method,
      headers: s.getHeadersMap(),
      body: s.body,
      mode: s.mode,
      interval: s.interval,
      count: s.count,
      stopTime: s.stopTime,
    };
    await invoke("save_profile", { name, profile });
    await loadProfiles();
  }, [loadProfiles]);

  const deleteProfile = useCallback(async (name: string) => {
    await invoke("delete_profile", { name });
    await loadProfiles();
  }, [loadProfiles]);

  const applyProfile = useCallback(async (name: string) => {
    const data = await invoke<Profile | null>("load_profile", { name });
    if (!data) return;
    store.applyProfile({
      url: data.url,
      method: data.method,
      mode: data.mode,
      interval: data.interval,
      count: data.count,
      stopTime: data.stopTime,
      headers: data.headers,
      body: data.body,
    });
  }, []);

  return { profiles, loadProfiles, saveProfile, deleteProfile, applyProfile };
}
