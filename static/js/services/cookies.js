// GMG Copyright (C) 2022 Alexandre Díaz
import {app, requestInfo} from "@gmg/base/app";
import {filter, isEmpty} from "underscore";
import Service from "@gmg/base/service";

export default class CookiesService extends Service {
  cookieStorageKeyPrefix = "cookie_consent_";
  #localStorage = null;
  #cookiesInfo = {
    [requestInfo.hostname]: {
      technical: {
        session: _("Registers a unique ID to store session data"),
      },
    },
    youtube: {
      "third-party": {
        CONSENT: _(
          "Used to detect if the visitor has accepted the marketing category in the cookie banner. This cookie is necessary for GDPR-compliance of the website."
        ),
        VISITOR_INFO1_LIVE: _(
          "Tries to estimate the user's bandwidth on pages with integrated YouTube videos."
        ),
        YSC: _(
          "Registers a unique ID to keep statistics of what videos from YouTube the user has seen."
        ),
      },
    },
    streamable: {
      "third-party": {
        muted: _("Used to remember if the video must be played muted."),
        volume: _("Used to remember the volume of the video."),
      },
    },
  };

  onWillStart() {
    this.#localStorage = app.getService("localStorage");
    return super.onWillStart();
  }

  accept(origins) {
    for (const origin of origins) {
      this.#localStorage.setItem(
        `${this.cookieStorageKeyPrefix}${origin}`,
        true
      );
    }
  }

  deny(origins) {
    for (const origin of origins) {
      this.#localStorage.setItem(
        `${this.cookieStorageKeyPrefix}${origin}`,
        false
      );
    }
  }

  /**
   * Check is the component has the cookies enabled
   *
   * @param {Array} origins
   * @param {Boolean} cancellable
   * @returns {Promise}
   */
  check(origins, cancellable = true) {
    if (isEmpty(origins)) {
      return Promise.resolve();
    }

    const origins_to_accept = this.#getOriginsToAccept(origins);
    const invalid_cookies = {};
    for (const origin of origins_to_accept) {
      invalid_cookies[origin] = this.#cookiesInfo[origin];
    }
    if (isEmpty(invalid_cookies)) {
      return Promise.resolve();
    }

    return this.displayAdvise(invalid_cookies, cancellable);
  }

  displayAdvise(cookies, cancellable) {
    return new Promise((resolve, reject) => {
      app.invokeComponent(
        "cookieModal",
        cookies,
        resolve,
        cancellable && reject
      );
    });
  }

  #getOriginsToAccept(origins) {
    return filter(
      origins,
      (origin) =>
        !this.#localStorage.getItem(`${this.cookieStorageKeyPrefix}${origin}`)
    );
  }
}
