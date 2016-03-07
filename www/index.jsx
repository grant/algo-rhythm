import React from 'react';
import ReactDOM from 'react-dom';
import $ from 'jquery';
import socket from './utils/socket';
import GeneratedMusicSection from './components/GeneratedMusicSection';
import SongGenerationSection from './components/SongGenerationSection';
import TrainingSection from './components/TrainingSection';
import UploadingSection from './components/UploadingSection';
import AppHeader from './components/AppHeader';
import DEBUG from './utils/debug';
import NotificationManager from './utils/NotificationManager';
import {OrderedSet} from 'immutable';
import {Notification, NotificationStack} from 'react-notification';


$(document).ready(function(){
  // Always be scrolled to the top on page load
  // TODO Doesn't work
  setTimeout(function() {
    $(this).scrollTop(0);
  }, 0);

  // Remove query parameters
  history.replaceState(null, "", location.href.split("?")[0]);
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
      },
      notifications: OrderedSet(),
      notificationCount: 0,
    };

    // Setup websockets
    socket.on('status', status => {
      if (DEBUG) {
        console.log('Updated status', status);
      }
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
        <NotificationStack
          notifications={this.state.notifications.toArray()}
          onDismiss={notification => this.setState({
            notifications: this.state.notifications.delete(notification)
          })}
        />
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

  addNotification(message) {
    const { notifications, notificationCount } = this.state;
    const id = notifications.size + 1;
    const newCount = notificationCount + 1;

    return this.setState({
      notificationCount: newCount,
      notifications: notifications.add({
        message: message,
        key: newCount,
        style: {
          bar: {
            backgroundColor: 'rgb(255, 89, 55)',
            color: 'white',
          },
        }
      })
    });
  }
}

let AppDOM = ReactDOM.render(<App />, document.querySelector("#app"));
NotificationManager.setMessageHandler((message) => {
  AppDOM.addNotification(message);
});
