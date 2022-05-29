/* eslint sort-imports: 0 */
// GMG Copyright (C) 2022 Alexandre Díaz
import {app, requestInfo} from "@gmg/base/app";

// Register services
import {
  LocalStorageService,
  SessionStorageService,
} from "@gmg/services/storage";
import CookiesService from "@gmg/services/cookies";
import RequestsService from "@gmg/services/requests";

app.registerService("requests", RequestsService);
app.registerService("localStorage", LocalStorageService);
app.registerService("sessionStorage", SessionStorageService);
app.registerService("cookies", CookiesService);

// Register components
import {
  Activity24hChart,
  Activity7dChart,
  AdminStatsPanel,
} from "@gmg/components/overview";
import {
  CookieModalWindow,
  LazyClick,
  LazyScroll,
  PrintEmail,
} from "@gmg/components/common";
import {UserActivity7dChart, UserWordCountChart} from "@gmg/components/user";
import Navbar from "@gmg/components/navbar";

app.registerComponent("navbar", Navbar);
app.registerComponent("adminStatsPanel", AdminStatsPanel);
app.registerComponent("activity7dChart", Activity7dChart);
app.registerComponent("activity24hChart", Activity24hChart);
app.registerComponent("userWordCountChart", UserWordCountChart);
app.registerComponent("userActivity7dChart", UserActivity7dChart);
app.registerComponent("lazyScroll", LazyScroll);
app.registerComponent("lazyClick", LazyClick);
app.registerComponent("printEmail", PrintEmail);
app.registerComponent("cookieModal", CookieModalWindow);

// On Start APP
window.addEventListener("load", () => {
  app.onWillStart().then(() => {
    app.onStart();
    const cookies = app.getService("cookies");
    cookies.check([requestInfo.hostname], false);
  });
});
// Window.addEventListener("unload", () => app.destroy());
