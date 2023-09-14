import { shallow } from 'enzyme';
import MuiTextField from '@material-ui/core/TextField';
import React from 'react';
import { TextInput, TextInputProps } from '../TextInput';

describe('<TextInput />', () => {
  it('should render with default props', () => {
    const element = shallow(<TextInput />);

    expect(element.find(MuiTextField)).toHaveLength(1);
    const muiInput = element.find(MuiTextField);
    const muiInputProps = muiInput.props();

    expect(muiInputProps.disabled).toBeFalsy();
    expect(muiInputProps.placeholder).toBe(undefined);
    expect(muiInputProps.value).toBe(undefined);
  });

  it('should render with custom props', () => {
    const props: TextInputProps = {
      disabled: true,
      placeholder: 'type...',
    };
    const element = shallow(<TextInput {...props} />);
    const renderedProps = element.props();

    expect(renderedProps.disabled).toBeTruthy();
    expect(renderedProps.placeholder).toBe('type...');
  });

  it('should render with defaultValue if it is provided', () => {
    const defaultValue = 'default value';
    const element = shallow(<TextInput defaultValue={defaultValue} />);
    const muiInput = element.find(MuiTextField);
    const muiInputProps = muiInput.props();

    expect(muiInputProps.defaultValue).toBe(defaultValue);
  });

  it('should call onChange callback if it is provided', () => {
    const mockOnChange = jest.fn();
    const mockChangeEvent = { target: { value: 'new value' } };
    const element = shallow(<TextInput onChange={mockOnChange} />);
    element.simulate('change', mockChangeEvent);

    expect(mockOnChange).toBeCalledWith(mockChangeEvent);
  });
});
