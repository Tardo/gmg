// GMG Copyright (C) 2022 Alexandre Díaz
import {debounce, defaults} from "underscore";
import $ from "jquery-slim";
import Component from "@gmg/base/component";
import ModalWindow from "@gmg/base/components/modal";
import {requestInfo} from "@gmg/base/app";

export class LazyComponent extends Component {
  useServices = ["cookies"];
  LAZY_ELEMENT_CLASS = "lazy";

  getNormalizedAttributes($elm, remove_attr = false) {
    const attrs = {};
    const elm_data = $elm.data();
    Object.keys(elm_data).forEach((dataName) => {
      if (dataName.startsWith("lazy")) {
        const targetAttributeName = dataName.replace(/^lazy/, "").toLowerCase();
        const targetAttributeValue = $elm.attr(targetAttributeName);
        const targetLazyAttributeValue = elm_data[dataName];
        if (
          !targetAttributeValue ||
          targetAttributeValue !== targetLazyAttributeValue
        ) {
          attrs[targetAttributeName] = targetLazyAttributeValue;
          if (remove_attr) {
            $elm.removeAttr(dataName);
          }
        }
      }
    });
    return attrs;
  }

  applyLazyAttributes($elm) {
    this.cookies
      .check(this.options.cookie_origins, this.options.cookie_cancellable)
      .then(() => {
        $elm.removeClass(this.LAZY_ELEMENT_CLASS);
        const attrs = this.getNormalizedAttributes($elm, true);
        const elm_data = $elm.data();
        if (elm_data?.createTag) {
          const $newElm = $(`<${elm_data.createTag}>`, attrs);
          $elm.replaceWith($newElm);
        } else {
          $elm.attr(attrs);
        }
      })
      .catch(() => {
        // Do nothing
      });
  }

  getLazyElements() {
    return this.$(`.${this.LAZY_ELEMENT_CLASS}`);
  }
}

export class LazyScroll extends LazyComponent {
  events = {
    scroll: this.#onScrollContainer,
  };

  constructor(parent, target, options) {
    super(...arguments);
    this.options = defaults(this.options, {
      bounce_time_scroll: 75,
      zone_y_offset: 150,
      zone_x_offset: 75,
    });
    this.load = debounce(
      this.#doLazyLoad.bind(this),
      this.options.bounce_time_scroll
    );
  }

  onStart() {
    super.onStart();
    this.#doLazyLoad();
  }

  #doLazyLoad() {
    this.getLazyElements().each((index, item) => {
      const $elm = $(item);
      if (!this.#isOptionVisible($elm)) {
        return;
      }
      this.applyLazyAttributes($elm);
    });
  }

  #getDimensions($elm) {
    const $offset = $elm.offset();
    const left = $offset.left;
    const top = $offset.top;
    const right = left + $elm.width();
    const bottom = top + $elm.height();
    return [left, top, right, bottom];
  }

  #isOptionVisible($elm) {
    let [ddViewLeft, ddViewTop, ddViewRight, ddViewBottom] =
      this.#getDimensions(this.$el);
    ddViewLeft -= this.options.zone_x_offset;
    ddViewTop -= this.options.zone_y_offset;
    ddViewRight += this.options.zone_x_offset;
    ddViewBottom += this.options.zone_y_offset;
    const [elemLeft, elemTop, elemRight, elemBottom] =
      this.#getDimensions($elm);
    return (
      elemLeft <= ddViewRight &&
      elemTop <= ddViewBottom &&
      elemRight >= ddViewLeft &&
      elemBottom >= ddViewTop
    );
  }

  #onScrollContainer() {
    this.load();
  }
}

export class LazyClick extends LazyComponent {
  events = {
    [`click .${this.LAZY_ELEMENT_CLASS}`]: this.#onClickLazy,
  };

  #onClickLazy(ev) {
    const $elm = $(ev.currentTarget);
    this.applyLazyAttributes($elm);
  }
}

export class PrintEmail extends Component {
  constructor(parent, target, options) {
    super(...arguments);
    this.options = defaults(this.options, {
      domain: requestInfo.hostname,
    });
  }

  onStart() {
    super.onStart();
    if (this.options.alias) {
      this.#printEmail();
    } else {
      console.error("Alias not defined!");
    }
  }

  #printObfuscate(text) {
    let res = "";
    for (const lett of text) {
      res += Math.random() < 0.5 ? `<span>${lett}</span>` : lett;
    }
    return res;
  }

  #printEmail() {
    const trast_at_text = _("at");
    let txt = this.#printObfuscate(this.options.alias);
    txt += ` <i>[${trast_at_text}]</i> `;
    txt += this.#printObfuscate(this.options.domain);
    this.$el.html(`&lt;${txt}&gt;`);
  }
}

export class CookieModalWindow extends ModalWindow {
  useServices = ["cookies"];

  constructor(parent, cookies, primaryCallback, secondaryCallback) {
    const origins = Object.keys(cookies);
    const trans_following_text = _("The following cookies will be created:");
    const trans_name_text = _("Name");
    const trans_desc_text = _("Description");
    let content = `<span>${trans_following_text}</span><br/>`;
    for (const origin of origins) {
      for (const section_name in cookies[origin]) {
        content += `<strong class="text-2xl mt-4 block capitalize">${origin} (${section_name})</strong><table class='table-auto border-collapse border border-slate-400 w-full'><thead><tr><th class='border border-slate-300 p-2'>${trans_name_text}</th><th class='border border-slate-300 p-2'>${trans_desc_text}</th></tr></thead><tbody>`;
        for (const cookie_name in cookies[origin][section_name]) {
          const cookie_def = cookies[origin][section_name][cookie_name];
          content += `<tr><td class='border border-slate-300 p-2'>${cookie_name}</td><td class='border border-slate-300 p-2'>${cookie_def}</td></tr>`;
        }
      }
      content += "</tbody></table>";
    }
    const options = {
      title: _("Cookie Management"),
      message: content,
      buttons: {
        primary: {
          callback: () => {
            this.cookies.accept(origins);
            if (primaryCallback) {
              primaryCallback();
            }
          },
        },
      },
    };
    if (secondaryCallback) {
      options.buttons.secondary = {
        label: _("Cancel"),
        callback: () => {
          this.cookies.deny(origins);
          secondaryCallback();
        },
      };
    }
    super(parent, null, options);
  }
}
