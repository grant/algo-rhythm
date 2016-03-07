import React from 'react';

export default class ProgressBar extends React.Component {
  static get defaultProps() {
    return {
      // generatedmusic: []
    }
  }

  render() {
    return (
      <div className="ProgressBar progress-bar">
        <div className="name">{this.props.name}</div>
        <div className="bar" style={`width: ${this.props.progress}%`}></div>
      </div>
    );
  }
}
