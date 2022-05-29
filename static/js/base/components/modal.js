// GMG Copyright (C) 2022 Alexandre Díaz
import $ from "jquery-slim";
import Component from "@gmg/base/component";

export default class ModalWindow extends Component {
  static ICONS = {
    success: `<div class="mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full bg-green-100 sm:mx-0 sm:h-10 sm:w-10">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
    </div>`,
    info: `<div class="mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full bg-blue-100 sm:mx-0 sm:h-10 sm:w-10">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-info" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
    </div>`,
    warning: `<div class="mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full bg-yellow-100 sm:mx-0 sm:h-10 sm:w-10">
        <svg class="h-6 w-6 text-yellow-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
    </div>`,
    danger: `<div class="mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full bg-red-100 sm:mx-0 sm:h-10 sm:w-10">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
    </div>`,
  };

  events = {
    "click .button-success": this.#onClickPrimary,
    "click .button-warning": this.#onClickSecondary,
  };

  constructor(parent, target, options) {
    const ooptions = $.extend(
      true,
      {
        title: "",
        message: "",
        backshadow: true,
        buttons: {
          primary: {
            label: _("Ok"),
            callback: null,
          },
        },
        type: "info",
        container: "body",
      },
      options
    );
    const otarget = `<div class="fixed z-10 inset-0 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
        <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity ${
              !ooptions.backshadow && "hidden"
            }" aria-hidden="true"></div>
            <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
            <div class="inline-block align-bottom bg-white text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full">
                <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                    <div class="sm:flex sm:items-start">
                        ${ModalWindow.ICONS[ooptions.type]}
                        <div class="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left grow">
                            <h3 class="text-lg leading-6 font-medium text-gray-900" id="modal-title">
                                ${ooptions.title}
                            </h3>
                            <div class="mt-2 text-sm text-gray-500">
                                ${ooptions.message}
                            </div>
                        </div>
                    </div>
                </div>
                <div class="bg-gray-50 px-4 py-3 grid ${
                  (ooptions.buttons.secondary && "grid-cols-2") || "grid-cols-1"
                } gap-2 mt-3">
                    <button type="button" class="w-full justify-center button button-success ${
                      ooptions.buttons.primary.className
                    }">
                        ${ooptions.buttons.primary.label}
                    </button>
                    <button type="button" class="w-full justify-center button button-warning ${
                      !ooptions.buttons.secondary && "hidden"
                    } ${
      ooptions.buttons.secondary && ooptions.buttons.secondary.className
    }">
                        ${
                          ooptions.buttons.secondary &&
                          ooptions.buttons.secondary.label
                        }
                    </button>
                </div>
            </div>
        </div>
    </div>`;
    super(parent, otarget, ooptions);
  }

  onWillStart() {
    return super.onWillStart(...arguments).then(() => {
      this.$el.appendTo(this.options.container);
    });
  }

  destroy() {
    super.onWillStart(...arguments);
    this.$el.remove();
  }

  #onClickPrimary() {
    if (this.options.buttons.primary && this.options.buttons.primary.callback) {
      this.options.buttons.primary.callback();
    }
    this.destroy();
  }

  #onClickSecondary() {
    if (
      this.options.buttons.secondary &&
      this.options.buttons.secondary.callback
    ) {
      this.options.buttons.secondary.callback();
    }
    this.destroy();
  }
}
