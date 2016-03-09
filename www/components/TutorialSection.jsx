import React from 'react';

export default class TutorialSection extends React.Component {
  render() {
    let {
      buttonName,
      onButtonClick,
      children,
      sectionName,
      tutorialSection,
    } = this.props;
    const inTutorial = (sectionName === tutorialSection);

    let childrenStyle = tutorialSection ? (inTutorial ? '' : 'not-current-tutorial') : '';
    return (
      <section className='TutorialSection'>
        <button
          className={'button nextButton ' + (inTutorial ? '' : 'invisible')}
          onClick={onButtonClick.bind(this, sectionName)}>
          {buttonName}
        </button>
        <div className={'fade-wrapper ' + childrenStyle}>
          {children}
        </div>
      </section>
    );
  }
}
