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
    let {
      training_configs,
      music_files
    } = this.props;

    return (
      <section className="TrainingSection section group" name="training">
        <TrainingProcess
          training_configs={training_configs} />
        <TrainConfig
          music_files={music_files} />
      </section>
    );
  }
}
