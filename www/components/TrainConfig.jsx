import React from 'react';
import $ from 'jquery';
import socket from '../utils/socket';

const STATE_DEFAULT = {
  name: '',
  iterations: 100,
  files: [],
};

export default class TrainConfig extends React.Component {
  static get propTypes() {
    return {
      music_files: React.PropTypes.array.isRequired,
    }
  }

  constructor(props) {
    super(props)
    this.state = STATE_DEFAULT;
  }

  render() {
    let music_files = this.props.music_files;
    let onSubmit = (e) => {
      e.preventDefault();

      // Convert form to object
      const valArray = $('.TrainConfig .form').serializeArray();
      let valObject = {};
      $(valArray).each((index, obj) => {
        // Make sure 'file' field is an array
        if (typeof valObject[obj.name] === 'undefined') {
          valObject[obj.name] = (obj.name === 'file') ? [obj.value] : obj.value;
        } else if (valObject[obj.name] instanceof Array) {
          valObject[obj.name].push(obj.value);
        }
      });

      // Reset fields
      this.setState(STATE_DEFAULT);

      socket.emit('train', valObject);
    }
    return (
      <section className="TrainConfig section train-config">
        <h1 className="title">Train Configuration</h1>
        <form
          onSubmit={onSubmit}
          action="/train"
          method="post"
          encType="multipart/form-data"
          className="form"
        >
          <ul>
            {music_files.length ? (
              music_files.map(file => {
                return (
                  <li key={file} className="file">
                    <label>
                      <input
                        type="checkbox"
                        name="file"
                        checked={this.state.files.indexOf(file) !== -1}
                        onChange={this.onCheckboxChange.bind(this, file)}
                        value={file} />
                      {file}
                    </label>
                  </li>
                );
              })
            ):(
              <li className="file none">No file to choose from</li>
            )}
          </ul>
          <h3 className="subtitle">Number of Iterations</h3>
          <input
            type="number"
            name="iterations"
            required="true"
            min="1"
            max="9999"
            value={this.state.iterations}
            onChange={this.onIterationsChange.bind(this)}
          />
          <h3 className="subtitle">Config Name</h3>
          <input
            type="text"
            value={this.state.name}
            name="name"
            required="true"
            onChange={this.onNameChange.bind(this)}
          />
          <input type="submit" value="Generate Config" />
        </form>
      </section>
    );
  }

  onNameChange(e) {
    this.setState({...this.state, name: e.target.value});
  }
  onIterationsChange(e) {
    this.setState({...this.state, iterations: e.target.value});
  }
  onCheckboxChange(file, e) {
    let files;
    if (this.state.files.indexOf(file) === -1) {
      files = this.state.files.concat(file)
    } else {
      files = this.state.files.slice(0);
      delete files[files.indexOf(file)];
    }
    this.setState({...this.state, files: files});
  }
}
