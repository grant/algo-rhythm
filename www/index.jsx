import React from 'react';
import ReactDOM from 'react-dom';
import $ from 'jquery';
import io from 'socket.io-client';
import GeneratedMusicSection from './components/GeneratedMusicSection';
import SongGenerationSection from './components/SongGenerationSection';
import TrainingSection from './components/TrainingSection';
import UploadingSection from './components/UploadingSection';
import AppHeader from './components/AppHeader';

$(document).ready(function(){
  // Always be scrolled to the top on page load
  // TODO Doesn't work
  setTimeout(function() {
    $(this).scrollTop(0);
  }, 0);

  // Remove query parameters
  history.replaceState(null, "", location.href.split("?")[0]);

  // Setup event handlers
  $('.section.generated-music .song:not(.header)').click(function() {
    var songName = $(this).data('name');
    console.log('toggle: ', songName);
    $(this).toggleClass('playing');
  });
});

export default class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      // The status object
      status: {
        generated_songs: [],
        generating_songs: [],
        music_files: [],
        trained_configs: [],
        training_configs: [],
      }
    };

    // Setup websockets
    var socket = io.connect();
    socket.on('status', status => {
      console.log('Updated status', status);
      this.setState({
        status: status,
      })
    });
  }

  render() {
    let {
      generated_songs,
      generating_songs,
      music_files,
      trained_configs,
      training_configs,
    } = this.state.status;
    return (
      <div className='App'>
        <AppHeader />
        <div className="content">
          <GeneratedMusicSection
            generated_songs={generated_songs} />
          <SongGenerationSection
            generating_songs={generating_songs}
            trained_configs={trained_configs} />
          <TrainingSection
            training_configs={training_configs}
            music_files={music_files} />
          <UploadingSection />
        </div>
      </div>
    );
  }
}

ReactDOM.render(<App/>, document.querySelector("#app"));
