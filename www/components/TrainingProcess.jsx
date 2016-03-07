import React from 'react';
import ProgressBar from './ProgressBar';

export default class TrainingProcess extends React.Component {
  static get propTypes() {
    return {
      training_configs: React.PropTypes.array.isRequired,
    }
  }

  render() {
    let training_configs = this.props.training_configs;
    return (
      <section className="TrainingProcess section training-configs">
        <h1 className="title">Configs Being Generated</h1>
        <ul>
          {training_configs.length ? (
            training_configs.map(config => {
              return (
                <li key={config.name} className="config">
                  <ProgressBar name={config.name} progress={config.process} />
                </li>
              );
            })
          ):(
            <li className="config none">No configs being trained</li>
          )}
        </ul>
      </section>
    );
  }
}
