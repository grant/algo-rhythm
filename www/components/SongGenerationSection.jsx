import React from 'react';
import SongGenerationProcesses from './SongGenerationProcesses';
import GenerateMusic from './GenerateMusic';

export default class SongGenerationSection extends React.Component {
  static get propTypes() {
    return {
      generating_songs: React.PropTypes.array.isRequired,
      trained_configs: React.PropTypes.array.isRequired,
    };
  }

  render() {
    return (
      <section className="SongGenerationSection section group" name="generating">
        <SongGenerationProcesses
          generating_songs={this.props.generating_songs} />
        <GenerateMusic
          trained_configs={this.props.trained_configs} />
      </section>
    );
  }
}
