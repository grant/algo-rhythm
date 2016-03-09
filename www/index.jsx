import React from 'react';
import ReactDOM from 'react-dom';
import $ from 'jquery';
import socket from './utils/socket';
import GeneratedMusicSection from './components/GeneratedMusicSection';
import SongGenerationSection from './components/SongGenerationSection';
import TrainingSection from './components/TrainingSection';
import UploadingSection from './components/UploadingSection';
import AppHeader from './components/AppHeader';
import TutorialSection from './components/TutorialSection';
import DEBUG from './utils/debug';
import NotificationManager from './utils/NotificationManager';
import {OrderedSet} from 'immutable';
import {Notification, NotificationStack} from 'react-notification';

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
      loading: true,
      // The current section of the tutorial
      tutorialSection: null,
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

  componentDidMount() {
    if (this.state.loading) {
      // Always be scrolled to the top on page load
      setTimeout(() => {
        this.setState({
          loading: false,
        });
      }, 1000);

      // Check browser url
      let query = location.href.split("?")[1] || '';
      if (query.indexOf('tutorial') !== -1) {
        this.startTutorial();
      }
      history.replaceState(null, "", location.href.split("?")[0]);
    }
  }

  startTutorial() {
    this.setState({
      tutorialSection: 'UploadingSection',
    });

    $('.App').animate({ scrollTop: $(document).height() }, "slow");
  }

  onTutorialButtonClick(sectionName) {
    if (sectionName === this.state.tutorialSection) {
      const tutorialOrder = [
        'UploadingSection',
        'TrainingSection',
        'SongGenerationSection',
        'GeneratedMusicSection',
      ];
      const nextTutorialSection = tutorialOrder[tutorialOrder.indexOf(sectionName) + 1] || null;
      // Scroll over to next section
      if (nextTutorialSection) {
        $('.App').animate({
          scrollTop: $('.' + nextTutorialSection).closest('.TutorialSection').position().top
        }, 1000);
      }
      this.setState({
        tutorialSection: nextTutorialSection,
      });
    }
  }

  render() {
    let {
      generated_songs,
      generating_songs,
      music_files,
      trained_configs,
      training_configs,
    } = this.state.status;

    let classNames = [
      'App',
      this.state.loading ? 'loading' : '',
      this.state.tutorialSection ? 'tutorial' : '',
    ].join(' ');

    return (
      <div className={classNames}>
        <NotificationStack
          notifications={this.state.notifications.toArray()}
          onDismiss={notification => this.setState({
            notifications: this.state.notifications.delete(notification)
          })}
        />
        <AppHeader />
        <div className="content">
          <nav className='nav'>
            <button onClick={this::startTutorial} className='button help'>Help</button>
          </nav>
          <TutorialSection
            buttonName={'Play your Music!'}
            onButtonClick={this::onTutorialButtonClick}
            sectionName={'GeneratedMusicSection'}
            tutorialSection={this.state.tutorialSection}>
            <GeneratedMusicSection
              onButtonClick={this::onTutorialButtonClick}
              tutorialSection={this.state.tutorialSection}
              generated_songs={generated_songs} />
          </TutorialSection>
          <TutorialSection
            buttonName={'Generate a Song'}
            onButtonClick={this::onTutorialButtonClick}
            sectionName={'SongGenerationSection'}
            tutorialSection={this.state.tutorialSection}>
            <SongGenerationSection
              generating_songs={generating_songs}
              trained_configs={trained_configs} />
          </TutorialSection>
          <TutorialSection
            buttonName={'Choose Songs for a New Config'}
            onButtonClick={this::onTutorialButtonClick}
            sectionName={'TrainingSection'}
            tutorialSection={this.state.tutorialSection}>
            <TrainingSection
              onButtonClick={this::onTutorialButtonClick}
              tutorialSection={this.state.tutorialSection}
              training_configs={training_configs}
              music_files={music_files} />
          </TutorialSection>
          <TutorialSection
            buttonName={'Upload a MusicXML file'}
            onButtonClick={this::onTutorialButtonClick}
            sectionName={'UploadingSection'}
            tutorialSection={this.state.tutorialSection}>
            <UploadingSection />
          </TutorialSection>
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
