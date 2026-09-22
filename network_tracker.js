if (!window.__rtkNetworkTracker) {
    window.__rtkNetworkTracker = { pending: 0, lastStatus: null, lastUrl: null };

    const origFetch = window.fetch;
    if (origFetch) {
        window.fetch = function(...args) {
            window.__rtkNetworkTracker.pending++;
            return origFetch.apply(this, args).then((response) => {
                window.__rtkNetworkTracker.pending--;
                window.__rtkNetworkTracker.lastStatus = response.status;
                window.__rtkNetworkTracker.lastUrl = response.url;
                return response;
            }).catch((err) => {
                window.__rtkNetworkTracker.pending--;
                throw err;
            });
        };
    }

    const OrigXHR = window.XMLHttpRequest;
    const origOpen = OrigXHR.prototype.open;
    const origSend = OrigXHR.prototype.send;
    OrigXHR.prototype.open = function(method, url, ...rest) {
        this.__rtkUrl = url;
        return origOpen.call(this, method, url, ...rest);
    };
    OrigXHR.prototype.send = function(...args) {
        window.__rtkNetworkTracker.pending++;
        this.addEventListener('loadend', () => {
            window.__rtkNetworkTracker.pending--;
            window.__rtkNetworkTracker.lastStatus = this.status;
            window.__rtkNetworkTracker.lastUrl = this.__rtkUrl;
        });
        return origSend.apply(this, args);
    };
}
