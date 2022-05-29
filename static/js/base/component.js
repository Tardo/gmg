// GMG Copyright (C) 2022 Alexandre Díaz
import $ from "jquery-slim";

export default class Component {
  useServices = [];
  fetchData = {};
  data = {};
  #parent = null;
  #childrens = [];

  constructor(parent, target, options) {
    // Force 'requests' service
    if (this.useServices.indexOf("requests") === -1) {
      this.useServices.push("requests");
    }
    this.options = options || {};
    this.setParent(parent);
    this.setElement(target);
  }

  onWillStart() {
    const tasks = [];
    for (const data_key in this.fetchData) {
      tasks.push(
        this.requests
          .postJSON(
            this.fetchData[data_key].endpoint,
            this.fetchData[data_key].data
          )
          .then((result) => {
            this.data[data_key] = result;
            return result;
          })
      );
    }
    return Promise.all(tasks);
  }

  onStart() {
    for (const cevent in this.events) {
      const [event_name, ...event_rest] = cevent.split(" ");
      const event_target = (event_rest && event_rest.join(" ")) || null;
      const $target = (event_target && this.$(event_target)) || this.$el;
      $target.on(event_name, this.events[cevent].bind(this));
    }
  }

  destroy() {
    if (this.#parent) {
      this.#parent.removeChildren(this);
    }
    for (const children of this.#childrens) {
      children.destroy();
    }
    this.#childrens = [];
    for (const cevent in this.events) {
      const [event_name, ...event_rest] = cevent.split(" ");
      const event_target = (event_rest && event_rest.join(" ")) || null;
      const $target = (event_target && this.$(event_target)) || this.$el;
      $target.off(event_name, this.events[cevent].bind(this));
    }
  }

  /**
   * @param {Component} parent
   */
  setParent(parent) {
    this.#parent = parent;
    if (this.#parent) {
      this.#parent.addChildren(this);
    }
  }

  /**
   * @returns {Component}
   */
  getParent() {
    return this.#parent;
  }

  addChildren(component) {
    this.#childrens.push(component);
  }

  removeChildren(component) {
    this.#childrens = $.grep(this.#childrens, (item) => item !== component);
  }

  setElement(target) {
    this.$el = $(target);
  }

  /**
   * Wrapper to call jquery 'find' method
   *
   * @param {String} selector
   * @returns {JQueryElement}
   */
  $(selector) {
    return this.$el.find(selector);
  }
}
