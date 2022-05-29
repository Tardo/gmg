// GMG Copyright (C) 2022 Alexandre Díaz
import ChartComponent from "@gmg/base/components/chart";
import Component from "@gmg/base/component";
import {defaults} from "underscore";
import {requestInfo} from "@gmg/base/app";

export class AdminStatsPanel extends Component {
  constructor(parent, target, options) {
    super(...arguments);
    this.options = defaults(this.options, {
      refresh_time: 15000,
    });
  }

  onStart() {
    super.onStart();
    if (requestInfo.session.logged_in) {
      window.setInterval(
        this.#onRefreshPrivate.bind(this),
        this.options.refresh_time
      );
      this.#onRefreshPrivate();
    }
    this.$cpuText = this.$("#cpu-usage");
    this.$cpuProgress = this.$("#cpu-usage-bar div");
    this.$memoryText = this.$("#memory-usage");
    this.$memoryProgress = this.$("#memory-usage-bar > div");
    this.$memoryCacheProgress = this.$("#memory-cache-usage-bar > div");
    this.$diskText = this.$("#disk-usage");
    this.$diskProgress = this.$("#disk-usage-bar > div");
    this.$uptimeText = this.$("#uptime");
  }

  #onRefreshPrivate() {
    this.#refreshMemoryHost();
    this.#refreshCPUHost();
    this.#refreshDiskHost();
    this.#refreshUptimeHost();
  }

  #refreshMemoryHost() {
    this.requests.postJSON("_refresh_memory_host").then((result) => {
      this.$memoryText.text(`${result.used} / ${result.total} MB`).fadeIn();
      this.$memoryProgress.css({width: `${result.percent}%`});
      this.$memoryProgress.text(_("In use:") + ` ${result.percent}%`);
      this.$memoryCacheProgress.css({width: `${result.percent_cached}%`});
      this.$memoryCacheProgress.text(
        _("Cache:") + ` ${result.percent_cached}%`
      );
    });
  }

  #refreshCPUHost() {
    this.requests.postJSON("_refresh_cpu_host").then((result) => {
      this.$cpuText.text(`${result}%`).fadeIn();
      this.$cpuProgress.css({width: `${result}%`});
    });
  }

  #refreshDiskHost() {
    this.requests.postJSON("_refresh_disk_host").then((result) => {
      this.$diskText
        .text(`${result.used} (${result.free} ${_("free")})`)
        .fadeIn();
      this.$diskProgress.css({width: result.percent});
      this.$diskProgress.text(_("Used:") + ` ${result.percent}`);
    });
  }

  #refreshUptimeHost() {
    this.requests.postJSON("_refresh_uptime_host").then((result) => {
      this.$uptimeText
        .text(
          _("Uptime:") +
            ` ${result.day} ` +
            _("day(s)") +
            ` ${String(result.hours).padStart(2, 0)}:${String(
              result.minutes
            ).padStart(2, 0)}`
        )
        .fadeIn();
    });
  }
}

export class Activity7dChart extends ChartComponent {
  chartName = "activity_7d";

  getConfig() {
    const values = this.data.chart;
    // Chart Data
    const data = {
      labels: values.labels,
      datasets: [
        {
          label: _("Posts"),
          data: values.values.posts,
          backgroundColor: "red",
          borderColor: "red",
        },
        {
          label: _("Users"),
          data: values.values.users,
          backgroundColor: "yellow",
          borderColor: "yellow",
        },
        {
          label: _("Mentions"),
          data: values.values.mentions,
          backgroundColor: "brown",
          borderColor: "brown",
        },
        {
          label: _("Replies"),
          data: values.values.replies,
          backgroundColor: "orange",
          borderColor: "orange",
        },
        {
          label: _("Medias"),
          data: values.values.medias,
          backgroundColor: "blue",
          borderColor: "blue",
        },
      ],
    };
    // Chart Config
    return {
      type: "line",
      data: data,
      options: {
        responsive: true,
        aspectRatio: false,
        plugins: {
          legend: {
            position: "none",
          },
          crosshair: {
            enabled: false,
            sync: {
              enabled: true,
            },
            zoom: {
              enabled: false,
            },
          },
          tooltip: {
            mode: "interpolate",
            intersect: false,
          },
        },
        scales: {
          y: {
            beginAtZero: true,
            grid: {
              color: this.mainColor,
              lineWidth: 1,
            },
            ticks: {
              color: this.mainColor,
            },
          },
          x: {
            grid: {
              color: this.mainColor,
              lineWidth: 1,
            },
            ticks: {
              color: this.mainColor,
            },
          },
        },
      },
    };
  }
}

export class Activity24hChart extends ChartComponent {
  chartName = "activity_24h";

  getConfig() {
    const values = this.data.chart;
    // Chart Data
    const data = {
      labels: values.labels,
      datasets: [
        {
          type: "line",
          label: _("Posts"),
          data: values.values.posts,
          backgroundColor: "red",
          borderColor: "red",
        },
        {
          label: _("Users"),
          data: values.values.users,
          backgroundColor: "yellow",
          borderColor: "yellow",
        },
        {
          label: _("Mentions"),
          data: values.values.mentions,
          backgroundColor: "brown",
          borderColor: "brown",
        },
        {
          label: _("Replies"),
          data: values.values.replies,
          backgroundColor: "orange",
          borderColor: "orange",
        },
        {
          label: _("Medias"),
          data: values.values.medias,
          backgroundColor: "blue",
          borderColor: "blue",
        },
      ],
    };
    // Chart Config
    return {
      type: "line",
      data: data,
      options: {
        responsive: true,
        aspectRatio: false,
        plugins: {
          legend: {
            position: "none",
          },
          crosshair: {
            enabled: false,
            sync: {
              enabled: true,
            },
            zoom: {
              enabled: false,
            },
          },
          tooltip: {
            mode: "interpolate",
            intersect: false,
          },
        },
        scales: {
          y: {
            beginAtZero: true,
            grid: {
              color: this.mainColor,
              lineWidth: 1,
            },
            ticks: {
              color: this.mainColor,
            },
          },
          x: {
            grid: {
              color: this.mainColor,
              lineWidth: 1,
            },
            ticks: {
              color: this.mainColor,
            },
          },
        },
      },
    };
  }
}
