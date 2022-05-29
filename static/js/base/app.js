// GMG Copyright (C) 2022 Alexandre Díaz
import $ from "jquery-slim";
import Component from "@gmg/base/component";

/** BootGMG **/
class MainApp extends Component {
  #registry = {
    components: {},
    services: {},
  };
  #services = {};

  constructor(parent, target, options, internal_data) {
    super(parent, target, options);
    this.__data = internal_data;
  }

  destroy() {
    super.destroy();
    const services = Object.values(this.#services);
    for (const service of services) {
      service.destroy();
    }
    this.#services = [];
    this.$el.off("click", "[class~='dropdown']");
    this.$el.off("click", "[data-dismiss]");
  }

  registerComponent(name, component) {
    if (Object.prototype.hasOwnProperty.call(this.#registry.components, name)) {
      console.warn(`Already exists a component called '${name}'!`);
      return;
    }
    this.#registry.components[name] = component;
  }
  getComponentClass(name) {
    return this.#registry.components[name];
  }
  invokeComponent(name, ...args) {
    const component_cls = this.getComponentClass(name);
    if (component_cls) {
      const component = new component_cls(this, ...args);
      this.#assignServices(component);
      component.onWillStart().then(() => {
        component.onStart();
      });
    } else {
      console.warn(`The component '${name}' don't exists!`);
    }
  }

  registerService(name, service) {
    if (Object.prototype.hasOwnProperty.call(this.#registry.services, name)) {
      console.warn(`Already exists a service called '${name}'!`);
      return;
    }
    this.#registry.services[name] = service;
  }
  getServiceClass(name) {
    return this.#registry.services[name];
  }
  getService(name) {
    return this.#services[name];
  }

  onWillStart() {
    return super
      .onWillStart()
      .then(() => {
        return this.#initializeServices();
      })
      .then(() => {
        return this.#initializeComponents();
      });
  }

  onStart() {
    super.onStart();
    // Assign core event
    this.$el.on(
      "click",
      "[class~='dropdown']",
      this.#onCoreClickDropdown.bind(this)
    );
    this.$el.on("click", "[data-dismiss]", this.#onCoreClickDismiss.bind(this));
  }

  #initializeServices() {
    for (const service_name in this.#registry.services) {
      this.#services[service_name] = new this.#registry.services[
        service_name
      ]();
    }
    const tasks = [];
    const service_names = Object.keys(this.#services);
    for (const service_name of service_names) {
      const service = this.#services[service_name];
      tasks.push(service.onWillStart());
    }
    return Promise.all(tasks);
  }

  #initializeComponents() {
    const tasks = [];
    const components = this.$("[data-component]");
    for (const elm of components) {
      const $el = $(elm);
      if (typeof $el.data("component_obj") !== "undefined") {
        continue;
      }
      const el_data = $el.data();
      const component_name = el_data.component;
      const component_cls = this.getComponentClass(component_name);
      const parent_component = $el.parents("[data-component]:first")[0];
      const parent_component_cls =
        parent_component && $(parent_component).data("component_obj");
      const component_options = {};
      Object.keys(el_data).forEach((optionName) => {
        if (optionName.startsWith("componentOption")) {
          const componentOptionName = optionName
            .replace(/^componentOption/, "")
            .toLowerCase();
          component_options[componentOptionName] = el_data[optionName];
        }
      });
      if (component_cls) {
        const component = new component_cls(
          parent_component_cls || this,
          $el,
          component_options
        );
        this.#assignServices(component);
        $el.data("component_obj", component);
        tasks.push(
          component.onWillStart().then(() => {
            component.onStart();
          })
        );
      } else {
        console.warn(_(`Can't found the '${component_name}' component!`), elm);
      }
    }

    return Promise.all(tasks);
  }

  #assignServices(component) {
    for (const service_name of component.useServices) {
      component[service_name] = this.#services[service_name];
    }
  }

  #onCoreClickDropdown(ev) {
    $($(ev.currentTarget).data("toggle")).toggleClass("hidden");
  }

  #onCoreClickDismiss(ev) {
    const classname = `.${$(ev.currentTarget).data("dismiss")}`;
    $(ev.currentTarget).closest(classname).remove();
  }
}

// This comes from templates/scripts/base_js
export const requestInfo = REQ_INFO;

export const app = new MainApp(null, $("body"));
