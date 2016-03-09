import React from 'react';
import $ from 'jquery';
import socket from '../utils/socket';
import NotificationManager from '../utils/NotificationManager';

const STATE_DEFAULT = {
  name: '',
  length: 60,
  config: null,
};

export default class GenerateMusic extends React.Component {
  static get propTypes() {
    return {
      trained_configs: React.PropTypes.array.isRequired,
    }
  }

  constructor(props) {
    super(props)
    this.state = STATE_DEFAULT;
  }

  render() {
    let trained_configs = this.props.trained_configs;
    let onSubmit = (e) => {
      e.preventDefault();

      // Convert form to object
      const valArray = $('.GenerateMusic .form').serializeArray();
      let valObject = {};
      $(valArray).each((index, obj) => {
        valObject[obj.name] = obj.value;
      });

      // Reset fields
      this.setState(STATE_DEFAULT);

      NotificationManager.sendMessage(`Generating song: "${valObject.name}"`);

      socket.emit('generate', valObject);
    }
    return (
      <section className="GenerateMusic section generate-music">
        <form
          onSubmit={onSubmit}
          action="/generate"
          method="post"
          encType="multipart/form-data"
          className="form"
        >
          <h1 className="title">Generate Music</h1>
          <h3 className="subtitle">Select a config</h3>
          <ul>
            {trained_configs.length ? (
              trained_configs.map(tc => {
                return (
                  <li key={tc}>
                    <label>
                      <input
                        type="radio"
                        name="config"
                        checked={this.state.config === tc}
                        onChange={this.onRadioChange.bind(this, tc)}
                        required={true}
                        value={tc} />
                      {tc}
                    </label>
                  </li>
                );
              })
            ):(
              <li className="config none">No configs available</li>
            )}
          </ul>
          <h3 className="subtitle">Select song length (seconds)</h3>
          <input
            type="number"
            required="true"
            name="length"
            min="1"
            max="999"
            value={this.state.length}
            onChange={::this.onLengthChange}
            />
          <h3 className="subtitle">Song name</h3>
          <input
            type="text"
            required="true"
            name="name"
            value={this.state.name}
            onChange={::this.onNameChange}
          />
          <input type="submit" value="Generate Song" />
        </form>
      </section>
    );
  }

  onNameChange(e) {
    this.setState({name: e.target.value});
  }
  onLengthChange(e) {
    this.setState({length: e.target.value});
  }
  onRadioChange(config, e) {
    this.setState({config: config});
  }
}
