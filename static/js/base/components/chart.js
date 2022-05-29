// GMG Copyright (C) 2022 Alexandre Díaz
import {Chart, Interaction, registerables} from "chart.js";
import {CrosshairPlugin, Interpolate} from "chartjs-plugin-crosshair";
import {WordCloudController, WordElement} from "chartjs-chart-wordcloud";
import Component from "@gmg/base/component";
import {requestInfo} from "@gmg/base/app";

Chart.register(...registerables);
Chart.register(CrosshairPlugin);
Chart.register(WordCloudController, WordElement);
Interaction.modes.interpolate = Interpolate;

export default class ChartComponent extends Component {
  chartName = null;
  chartOptions = null;
  #chart = null;
  mainColor = "rgb(171,171,171)";

  onWillStart() {
    this.fetchData.chart = {
      endpoint: "/get_chart_data",
      data: {
        site_id: requestInfo.session.site_id,
        name: this.chartName,
        options: this.chartOptions || {},
      },
    };
    return super.onWillStart(...arguments);
  }

  getConfig() {
    return null;
  }

  getChart() {
    return this.#chart;
  }

  onStart() {
    super.onStart(...arguments);
    this.renderChart();
  }

  destroy() {
    if (this.#chart) {
      this.#chart.destroy();
    }
    super.destroy(...arguments);
  }

  renderChart() {
    const config = this.getConfig();
    if (
      config &&
      config.data.datasets.length &&
      config.data.datasets[0].data.length
    ) {
      this.#chart = new Chart(this.$el, config);
    } else {
      console.warn(_("Can't render the graph. No config or data given!"));
    }
  }
}
