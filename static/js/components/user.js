// GMG Copyright (C) 2022 Alexandre Díaz
import ChartComponent from "@gmg/base/components/chart";
import {WordCloudController} from "chartjs-chart-wordcloud";

export class UserActivity7dChart extends ChartComponent {
  chartName = "user_activity_7d";

  constructor(parent, target, options) {
    super(...arguments);
    this.chartOptions = {
      user_id: options.user_id,
    };
  }

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
          label: _("Threads"),
          data: values.values.threads,
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

export class UserWordCountChart extends ChartComponent {
  chartName = "user_word_count";

  constructor(parent, target, options) {
    super(...arguments);
    this.chartOptions = {
      user_id: options.user_id,
    };
  }

  getConfig() {
    const values = this.data.chart;
    const max_count = Math.max(...values.count);
    // Chart Data
    const data = {
      labels: values.words,
      datasets: [
        {
          label: _("weight"),
          data: values.count.map((item) => (item / max_count) * 60 + 5),
          color: this.mainColor,
        },
      ],
    };
    // Chart Config
    return {
      type: WordCloudController.id,
      data: data,
      options: {
        responsive: true,
        aspectRatio: false,
        plugins: {
          legend: {
            position: "none",
          },
          crosshair: false,
        },
      },
    };
  }
}
