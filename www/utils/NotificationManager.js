let messageHandler = () => {};

export default class NotificationManager {
  static setMessageHandler(handler) {
    messageHandler = handler;
  }
  static sendMessage(message) {
    messageHandler(message);
  }
}
