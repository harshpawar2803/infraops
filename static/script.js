let cpuData = [];
let memData = [];
let diskData = [];
let labels = [];

function createChart(id, label) {
    return new Chart(document.getElementById(id), {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: label,
                data: [],
                borderWidth: 2
            }]
        },
        options: {
            scales: {
                y: {
                    min: 0,
                    max: 100
                }
            }
        }
    });
}

let cpuChart = createChart("cpuChart", "CPU %");
let memChart = createChart("memChart", "Memory %");
let diskChart = createChart("diskChart", "Disk %");

function updateChart(chart, data) {
    chart.data.labels = labels;
    chart.data.datasets[0].data = data;
    chart.update();
}

function popupAlert(msg) {
    alert("SKYNET ALERT: " + msg);
}

let oldFailed = "";
let oldSSH = "";

function loadStats() {
    fetch("/api/stats")
    .then(res => res.json())
    .then(data => {

        // ==========================
        // System Information
        // ==========================
        document.getElementById("hostname").innerText = data.hostname || "-";
        document.getElementById("os").innerText = data.os || "-";
        document.getElementById("kernel").innerText = data.kernel || "-";
        document.getElementById("architecture").innerText = data.architecture || "-";
        document.getElementById("ip").innerText = data.ip || "-";
        document.getElementById("uptime").innerText = data.uptime || "-";

        // ==========================
        // AWS EC2 Information
        // ==========================
        document.getElementById("instance_id").innerText =
            data.instance_id || "Local Machine";

        document.getElementById("instance_type").innerText =
            data.instance_type || "-";

        document.getElementById("region").innerText =
            data.region || "-";

        document.getElementById("availability_zone").innerText =
            data.availability_zone || "-";

        // ==========================
        // CPU
        // ==========================
        document.getElementById("cpu").innerText = data.cpu + "%";
        document.getElementById("cpu").className = data.cpu_color;

        // ==========================
        // Memory
        // ==========================
        document.getElementById("memory").innerText = data.memory + "%";
        document.getElementById("memory").className = data.memory_color;

        // ==========================
        // Disk
        // ==========================
        document.getElementById("disk").innerText = data.disk + "%";
        document.getElementById("disk").className = data.disk_color;

        // ==========================
        // Load Average
        // ==========================
        if (Array.isArray(data.loadavg)) {
            document.getElementById("loadavg").innerText =
                data.loadavg.join("  |  ");
        } else {
            document.getElementById("loadavg").innerText = data.loadavg;
        }

        // ==========================
        // Users
        // ==========================
        document.getElementById("users").innerText =
            data.users || "No users logged in";

        document.getElementById("ssh_users").innerText =
            data.ssh_users || "No SSH users";

        // ==========================
        // Running Services
        // ==========================
        let serviceText = "";

        for (const service in data.services) {
            serviceText +=
                service.toUpperCase() +
                " : " +
                data.services[service] +
                "\n";
        }

        document.getElementById("services").innerText = serviceText;

        // ==========================
        // Alerts
        // ==========================
        if (data.cpu > 80) popupAlert("High CPU Usage");

        if (data.memory > 80) popupAlert("High Memory Usage");

        if (data.disk > 80) popupAlert("High Disk Usage");

        // ==========================
        // Charts
        // ==========================
        let now = new Date().toLocaleTimeString();

        labels.push(now);
        cpuData.push(data.cpu);
        memData.push(data.memory);
        diskData.push(data.disk);

        if (labels.length > 10) {
            labels.shift();
            cpuData.shift();
            memData.shift();
            diskData.shift();
        }

        updateChart(cpuChart, cpuData);
        updateChart(memChart, memData);
        updateChart(diskChart, diskData);

    })
    .catch(err => {
        console.error(err);
    });
}
function loadAuth() {
    fetch("/api/auth")
    .then(res => res.json())
    .then(data => {
        document.getElementById("failed").innerText = data.failed;
        document.getElementById("success").innerText = data.success;
        document.getElementById("telnet").innerText = data.telnet;

        if (oldFailed !== "" && data.failed !== oldFailed) {
            popupAlert("New failed password attempt detected");
        }

        if (oldSSH !== "" && data.success !== oldSSH) {
            popupAlert("New SSH login detected");
        }

        oldFailed = data.failed;
        oldSSH = data.success;
    });
}

function loadLogs() {
    let q = document.getElementById("search").value;
    fetch("/api/logs?q=" + q)
    .then(res => res.json())
    .then(data => {
        document.getElementById("logs").innerText = data.logs;
    });
}

setInterval(loadStats, 5000);
setInterval(loadAuth, 5000);
setInterval(loadLogs, 10000);

loadStats();
loadAuth();
loadLogs();

