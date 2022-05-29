// GMG Copyright (C) 2022 Alexandre Díaz
import $ from "jquery-slim";
import Component from "@gmg/base/component";

export default class Navbar extends Component {
  events = {
    "change #flexSwitchCheckDarkTheme": this.#onClickDarkThemeSwitch,
  };

  onStart() {
    super.onStart();
    this.$localTime = this.$("#localtime");
    this.$localZone = this.$("#localzone");
    this.$tzForm = this.$("#tzform");
    window.setInterval(this.#onRefreshTimer.bind(this), 30000);
    this.#onRefreshTimer();
  }

  #updateHostLocalTime() {
    this.requests.postJSON("/_refresh_host_localtime").then((result) => {
      this.$localTime.text(result.localtime);
      this.$localZone.text(result.localzone);
    });
  }

  #onRefreshTimer() {
    this.#updateHostLocalTime();
  }

  #onClickDarkThemeSwitch(ev) {
    const is_dark = !$(ev.currentTarget).is(":checked");
    this.requests
      .postJSON("/_set_dark_theme", {enable: is_dark})
      .then((result) => {
        if (result.success) {
          $("html").toggleClass("dark", is_dark);
        }
      });
  }

  #onChangeTZ() {
    this.requests
      .postJSON("/_set_timezone", this.$tzForm.serialize())
      .then((result) => {
        if (result.success) {
          window.location.reload();
        }
      });
  }
}
