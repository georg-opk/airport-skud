const CV_BASE = "http://localhost:8000/api/v1";
const CHECKPOINT_ID = 1;
const LIVENESS_THRESHOLD = 0.5;

class CameraVerification {
    constructor() {
        this.video = document.getElementById("camera-video");
        this.canvas = document.getElementById("capture-canvas");
        this.stream = null;
        this.busy = false;
        this.autoTimer = null;
        this.autoActive = false;
        this.log = [];
        this.counters = {grant: 0, reject: 0, attack: 0};
        this.onCounters = null;
        window.addEventListener("beforeunload", () => this.stopCamera());
    }

    async startCamera() {
        if (this.stream) return;
        try {
            this.stream = await navigator.mediaDevices.getUserMedia({
                video: {width: {ideal: 640}, height: {ideal: 480}}, audio: false
            });
            this.video.srcObject = this.stream;
            await this.video.play();
            this._status("Камера активна", "ok");
        } catch (e) {
            console.error(e);
            this._status("Камера недоступна: " + e.message, "danger");
        }
    }

    captureBlob() {
        const w = this.video.videoWidth || 640;
        const h = this.video.videoHeight || 480;
        this.canvas.width = w;
        this.canvas.height = h;
        this.canvas.getContext("2d").drawImage(this.video, 0, 0, w, h);
        return new Promise((res) => this.canvas.toBlob(res, "image/jpeg", 0.9));
    }

    async identifyFrame() {
        if (!this.stream || this.busy) return;
        this.busy = true;
        this._spinner(true);
        try {
            const blob = await this.captureBlob();
            const fd = new FormData();
            fd.append("frame", blob, "frame.jpg");
            const headers = {};
            const token = localStorage.getItem("token");
            if (token) headers["Authorization"] = "Bearer " + token;
            const res = await fetch(
                CV_BASE + "/cv/identify?checkpoint_id=" + CHECKPOINT_ID,
                {method: "POST", headers, body: fd});
            if (!res.ok) throw new Error("HTTP " + res.status);
            const data = await res.json();
            this._render(data);
            this._count(data);
            this._addLog(data);
        } catch (e) {
            console.error(e);
            this._status("Ошибка обработки кадра: " + e.message, "danger");
        } finally {
            this.busy = false;
            this._spinner(false);
        }
    }

    toggleAuto() {
        if (this.autoActive) {
            this.stopAuto();
        } else {
            this.startAuto(2500);
        }
    }

    startAuto(ms) {
        this.stopAuto();
        this.autoTimer = setInterval(() => this.identifyFrame(), ms);
        this.autoActive = true;
        this._updateAutoBtn();
        this._status("Автозахват включён (каждые " + (ms / 1000) + " с)", "ok");
    }

    stopAuto() {
        if (this.autoTimer) {
            clearInterval(this.autoTimer);
            this.autoTimer = null;
        }
        this.autoActive = false;
        this._updateAutoBtn();
        if (this.stream) this._status("Автозахват выключен", "");
    }

    _updateAutoBtn() {
        const btn = document.getElementById("btn-auto");
        if (!btn) return;
        btn.textContent = this.autoActive ? "Стоп захвата" : "Автозахват";
        btn.style.background = this.autoActive ? "#b5443a" : "#3a4a63";
    }

    stopCamera() {
        this.stopAuto();
        if (this.stream) {
            this.stream.getTracks().forEach((t) => t.stop());
            this.stream = null;
            if (this.video) this.video.srcObject = null;
            this._status("Камера остановлена", "");
        }
    }

    _render(r) {
        const box = document.getElementById("verify-result");
        if (!box) return;
        const liveness = r.liveness_score ?? 0;
        const sim = r.similarity ?? 0;
        if (liveness < LIVENESS_THRESHOLD && r.reason === "attack") {
            box.className = "verify-result attack";
            box.textContent = "АТАКА ПРЕДСТАВЛЕНИЯ (живость " + liveness.toFixed(2) + ")";
        } else if (r.decision === "grant") {
            box.className = "verify-result grant";
            box.textContent = "ДОПУСК — сотрудник #" + r.employee_id + " (сходство " + sim.toFixed(2) + ")";
        } else {
            box.className = "verify-result reject";
            box.textContent = "ОТКАЗ — " + this._reasonText(r.reason);
        }
    }

    _reasonText(reason) {
        return ({
                no_face: "лицо не обнаружено", no_match: "нет совпадения",
                attack: "атака представления", bad_frame: "некорректный кадр",
                cv_unavailable: "CV-сервис недоступен", cv_error: "ошибка обработки"
            }
        )[reason] || (reason || "нет совпадения");
    }

    _classify(r) {
        const liveness = r.liveness_score ?? 0;
        if (liveness < LIVENESS_THRESHOLD && r.reason === "attack") return "attack";
        if (r.decision === "grant") return "grant";
        return "reject";
    }

    _count(r) {
        const kind = this._classify(r);
        this.counters[kind] = (this.counters[kind] || 0) + 1;
        if (typeof this.onCounters === "function") {
            this.onCounters({grant: this.counters.grant, reject: this.counters.reject, attack: this.counters.attack});
        }
    }

    _addLog(r) {
        var now = new Date();
        var dt = now.toLocaleDateString("ru-RU") + " " + now.toLocaleTimeString("ru-RU");
        var tbody = document.getElementById("verify-log-body");
        if (!tbody) return;

        // убираем заглушку
        var empty = tbody.querySelector(".logs-empty");
        if (empty) empty.parentElement.removeChild(empty);

        var sim = (r.similarity != null ? r.similarity : 0).toFixed(2);
        var live = (r.liveness_score != null ? r.liveness_score : 0).toFixed(2);
        var decision = r.decision === "grant" ? "Допуск" : "Отказ";
        var rowCls = "row-reject";
        if (r.decision === "grant") rowCls = "row-grant";
        else if (r.reason === "attack") rowCls = "row-attack";
        var tr = document.createElement("tr");
        tr.className = rowCls;
        tr.innerHTML =
            "<td>" + dt + "</td>" +
            "<td>КПП-" + CHECKPOINT_ID + "</td>" +
            "<td>" + decision + "</td>" +
            "<td>" + (r.employee_id != null ? r.employee_id : "—") + "</td>" +
            "<td>" + sim + "</td>" +
            "<td>" + live + "</td>" +
            "<td>" + (r.reason || "") + "</td>";
        if (tbody.firstChild) {
            tbody.insertBefore(tr, tbody.firstChild);
        } else {
            tbody.appendChild(tr);
        }
        while (tbody.children.length > 50) {
            tbody.removeChild(tbody.lastChild);
        }
    }

    _spinner(on) {
        var s = document.getElementById("verify-spinner");
        if (s) s.style.display = on ? "inline-block" : "none";
    }

    _status(text, cls) {
        var s = document.getElementById("verify-status");
        if (s) {
            s.textContent = text;
            s.className = "verify-status " + (cls || "");
        }
    }
}