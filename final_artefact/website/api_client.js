(function () {
    function fallbackEscapeHtml(value) {
        return String(value ?? "-")
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll('"', "&quot;")
            .replaceAll("'", "&#39;");
    }

    function parseResponseError(raw, status, path) {
        let message = `Request failed (${status})`;

        if (raw) {
            try {
                const payload = JSON.parse(raw);
                if (payload && typeof payload === "object" && payload.error) {
                    message = String(payload.error);
                } else {
                    message = raw;
                }
            } catch {
                message = raw;
            }
        }

        if (status === 404 && String(path || "").startsWith("/api/pipeline/")) {
            return "Pipeline API endpoints are unavailable. Restart the website server so the latest API routes are loaded.";
        }

        return message;
    }

    async function fetchJson(path, options = undefined, config = undefined) {
        const effectiveConfig = config && typeof config === "object" ? config : {};
        let response;

        try {
            response = await fetch(path, options);
        } catch {
            if (effectiveConfig.networkMessage) {
                throw new Error(String(effectiveConfig.networkMessage));
            }
            throw new Error("Local API is unreachable. Start via setup/start_website.cmd and refresh this page.");
        }

        if (!response.ok) {
            const raw = await response.text();
            throw new Error(parseResponseError(raw, response.status, path));
        }

        return response.json();
    }

    window.WebsiteApi = {
        fetchJson,
        escapeHtml: fallbackEscapeHtml
    };
})();
