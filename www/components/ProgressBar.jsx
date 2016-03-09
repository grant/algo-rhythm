import React from 'react';

export default class ProgressBar extends React.Component {
  static get propTypes() {
    return {
      name: React.PropTypes.string.isRequired,
      progress: React.PropTypes.number.isRequired,
    };
  }

  render() {
    let progressBarName = this.props.name + ` (${this.props.progress}%)`;
    return (
      <div className="ProgressBar progress-bar">
        <div className="name">{progressBarName}</div>
        <div className="bar" style={{width: this.props.progress + '%'}}></div>
      </div>
    );
  }
}
