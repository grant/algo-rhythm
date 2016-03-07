import React from 'react';

export default class UploadingSection extends React.Component {
  static get defaultProps() {
    return {
      // generatedmusic: []
    }
  }

  render() {
    return (
      <section className="UploadingSection section group uploading">
        <section className="section upload">
          <h1 className="title">Upload MusicXML</h1>
          <form action="/upload" method="post" encType="multipart/form-data" className="form">
            <label className="button">
              <input type="file" name="file"/>
              Upload MusicXML File
            </label>
          </form>
        </section>
      </section>
    );
  }
}
