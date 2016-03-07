import React from 'react';

export default class GenerateMusic extends React.Component {
  static get propTypes() {
    return {
      trained_configs: React.PropTypes.array.isRequired,
    }
  }

  render() {
    let trained_configs = this.props.trained_configs;
    return (
      <section className="GenerateMusic section generate-music">
        <form action="/generate" method="post" encType="multipart/form-data" className="form">
          <h1 className="title">Generate Music</h1>
          <h3 className="subtitle">Select a config</h3>
          <ul>
            {trained_configs.length ? (
              trained_configs.map(tc => {
                return (
                  <li key={tc}>
                    <label>
                      <input type="radio" name="config" value="{tc}" />
                      {tc}
                    </label>
                  </li>
                );
              })
            ):(
              <li className="config none">No configs available</li>
            )}
          </ul>
          <h3 className="subtitle">Select song length (seconds)</h3>
          <input type="number" required="true" name="length" min="1" max="999" />
          <h3 className="subtitle">Song name</h3>
          <input type="text" required="true" name="name" />
          <input type="submit" value="Generate Song" />
        </form>
      </section>
    );
  }
}
