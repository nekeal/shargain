const STORAGE_KEY = 'shargain_selected_target_id';

export function loadStoredTargetId(): number | null {
    try {
        const stored = localStorage.getItem(STORAGE_KEY);
        if (stored === null) return null;
        const parsed = parseInt(stored, 10);
        return Number.isFinite(parsed) ? parsed : null;
    } catch {
        return null;
    }
}

export function saveStoredTargetId(targetId: number) {
    try {
        localStorage.setItem(STORAGE_KEY, String(targetId));
    } catch {
        // localStorage not available
    }
}
