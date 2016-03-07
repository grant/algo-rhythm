import React from 'react';

export default class TrainConfig extends React.Component {
  static get propTypes() {
    return {
      music_files: React.PropTypes.array.isRequired,
    }
  }

  render() {
    let music_files = this.props.music_files;
    return (
      <section className="TrainConfig section train-config">
        <h1 className="title">Train Configuration</h1>
        <form action="/train" method="post" encType="multipart/form-data" className="form">
          <ul>
            {music_files.length ? (
              music_files.map(file => {
                return (
                  <li key={file} className="file">
                    <label>
                      <input type="checkbox" name="file" value="{file}" />
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
          <input type="number" name="iterations" required="true" min="1" max="9999" />
          <h3 className="subtitle">Config Name</h3>
          <input type="text" name="name" required="true" />
          <input type="submit" value="Generate Config" />
        </form>
      </section>
    );
  }
}
