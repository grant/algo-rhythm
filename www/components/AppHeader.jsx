import React from 'react';

export default class AppHeader extends React.Component {
  render() {
    return (
      <header className='AppHeader header'>
        <img src="static/img/logo.svg" alt="Algo Rhythm" className="logo" />
      </header>
    );
  }
}
