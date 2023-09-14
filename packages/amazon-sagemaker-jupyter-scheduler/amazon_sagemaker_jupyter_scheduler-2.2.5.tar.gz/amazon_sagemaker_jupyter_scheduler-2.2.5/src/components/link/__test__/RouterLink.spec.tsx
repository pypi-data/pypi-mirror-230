import { shallow } from 'enzyme';
import React from 'react';
import { RouterLink, RouterLinkProps } from '../RouterLink';
import { LinkUnderline } from '../types';

describe('<RouterLink />', () => {
  const to = '/user';
  const defaultProps: RouterLinkProps = {
    disabled: false,
    underline: LinkUnderline.Always,
    to: to,
  };

  it('renders correctly with default props', () => {
    const props = defaultProps;
    const label = 'label';
    const test = shallow(<RouterLink {...props}>{label}</RouterLink>);

    expect(test.text()).toBe(label);
    expect(test.props().to).toBe(to);
  });
});
