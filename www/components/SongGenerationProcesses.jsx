import React from 'react';
import ProgressBar from './ProgressBar';

export default class SongGenerationProcesses extends React.Component {
  static get propTypes() {
    return {
      generating_songs: React.PropTypes.array.isRequired,
    }
  }

  render() {
    let generating_songs = this.props.generating_songs;
    return (
      <section className="SongGenerationProcesses section song-generation-processes">
        <h1 className="title">Songs Being Generated</h1>
        <ul>
          {generating_songs.length ? (
            generating_songs.map(song => {
              return (
                <li key={song.name} className="song">
                  <ProgressBar name={song.name} progress={song.progress} />
                </li>
              );
            })
          ): (
            <li className="song none">No music being generated</li>
          )}
        </ul>
      </section>
    );
  }
}
