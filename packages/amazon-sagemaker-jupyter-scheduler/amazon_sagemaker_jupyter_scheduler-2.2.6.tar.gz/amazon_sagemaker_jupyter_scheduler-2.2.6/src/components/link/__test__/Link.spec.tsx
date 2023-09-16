import { shallow } from 'enzyme';
import React from 'react';
import { Link, LinkProps } from '../Link';
import { LinkTarget, LinkUnderline } from '../types';

describe('<Link />', () => {
  const children = 'Test';
  const href = 'https://www.amazon.com';
  const defaultProps: LinkProps = {
    children,
    href,
    underline: LinkUnderline.Hover,
    target: LinkTarget.External,
  };

  it('renders correctly with default props', () => {
    const props = { ...defaultProps };
    const element = shallow(<Link {...props} />);

    expect(element.text()).toBe(children);
    expect(element.props().href).toBe(href);
  });

  it('should handle onClick callback function properly', () => {
    const mockedClickEvent = { target: {} };
    const onClickHandler = jest.fn();
    const props = { ...defaultProps, onClick: onClickHandler };
    const element = shallow(<Link {...props} />);

    element.simulate('click', mockedClickEvent);

    expect(onClickHandler).toHaveBeenCalledTimes(1);
  });
});
