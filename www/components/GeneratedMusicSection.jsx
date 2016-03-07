import React from 'react';

export default class GeneratedMusicSection extends React.Component {
  static get propTypes() {
    return {
      generated_songs: React.PropTypes.array.isRequired,
    };
  }

  render() {
    let generated_songs = this.props.generated_songs;
    return (
      <section className="section generated-music">
        <h1 className="title">Generated Songs</h1>
        {!generated_songs.length ? (
          <div className="song none">No songs have been generated yet.</div>
        ):(
          <ul className="song-list">
            <li className="song header">
              <span className="cell icon"></span>
              <span className="cell name">Song Name</span>
              <span className="cell length">Length</span>
            </li>
            {generated_songs.map(song => {
              return (
                <li key={song.name} className="song" data-name="{song.name}">
                  <span className="cell icon">
                    <span className="play">▶</span>
                    <span className="stop">■</span>
                  </span>
                  <span className="cell name">{song.name}</span>
                  <span className="cell length">{song.length}</span>
                </li>
              );
            })}
          </ul>
        )}
      </section>
    );
  }
}
