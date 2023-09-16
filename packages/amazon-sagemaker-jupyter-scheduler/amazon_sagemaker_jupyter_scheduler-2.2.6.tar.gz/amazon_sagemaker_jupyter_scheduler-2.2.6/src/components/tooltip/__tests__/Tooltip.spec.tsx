import React from 'react';
import { shallow, ShallowWrapper } from 'enzyme';
import { Tooltip } from '../Tooltip';
import MuiTooltip from '@material-ui/core/Tooltip';

const tooltipText = 'This is a tooltip';
const childTestId = 'child-test-id';
const testId = 'test-id';

const renderComponent = (): ShallowWrapper => {
  return shallow(
    <Tooltip id={testId} title={tooltipText}>
      <span id={childTestId}></span>
    </Tooltip>,
  );
};

describe('<Tooltip />', () => {
  let wrapper: ShallowWrapper;
  beforeAll(() => {
    wrapper = renderComponent();
  });

  it('should render the tooltip with children', () => {
    expect(wrapper.find(MuiTooltip)).toHaveLength(1);
    expect(wrapper.find(`#${childTestId}`)).toHaveLength(1);
  });

  it('should show tooltip on hover', () => {
    wrapper.simulate('mouseover');
    setTimeout(() => {
      expect(wrapper.state('open')).toBe(true);
    }, 0);

    wrapper.simulate('mouseleave');
    setTimeout(() => {
      expect(wrapper.state('open')).toBe(false);
    }, 0);
  });
});
