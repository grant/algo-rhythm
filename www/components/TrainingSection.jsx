import React from 'react';
import TrainingProcess from './TrainingProcess';
import TrainConfig from './TrainConfig';

export default class TrainingSection extends React.Component {
  static get propTypes() {
    return {
      training_configs: React.PropTypes.array.isRequired,
      music_files: React.PropTypes.array.isRequired,
    }
  }

  render() {
    return (
      <section className="TrainingSection section group training" name="training">
        <TrainingProcess
          training_configs={this.props.training_configs} />
        <TrainConfig
          music_files={this.props.music_files} />
      </section>
    );
  }
}
