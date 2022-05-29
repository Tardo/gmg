// GMG Copyright (C) 2022 Alexandre Díaz

export default class Service {
  onWillStart() {
    return Promise.resolve();
  }

  destroy() {
    throw Error("Not Implemented!");
  }
}
