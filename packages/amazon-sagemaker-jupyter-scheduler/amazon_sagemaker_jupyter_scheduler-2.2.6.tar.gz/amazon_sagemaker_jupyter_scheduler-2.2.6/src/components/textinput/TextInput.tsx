import React from 'react';
import { TextField as MuiTextField, TextFieldProps as MuiTextFieldProps } from '@material-ui/core';
import { cx } from '@emotion/css';
import { formHelperTextStyles, inputStyles, TextInputBase } from './styles';
import { TextInputSize } from './types';
// import { InputLabelProps } from '@material-ui/core/InputLabel';
import { InputProps } from '@material-ui/core/Input';

export interface TextInputProps extends Omit<MuiTextFieldProps, 'children' | 'color' | 'size' | 'InputProps'> {
  readonly size?: TextInputSize;
  readonly InputProps?: Partial<InputProps>;
}

const TextInput: React.FunctionComponent<TextInputProps> = ({
  classes,
  className,
  InputProps,
  FormHelperTextProps,
  size = TextInputSize.Medium,
  variant,
  ...materialTextFieldProps
}) => {
  const classNames = cx(TextInputBase(), className, classes?.root);
  return (
    <MuiTextField
      classes={{ root: classNames, ...classes }}
      variant={variant}
      InputProps={{
        ...InputProps,
        classes: {
          root: cx(inputStyles({ size }).root, InputProps?.classes?.root),
          input: cx(inputStyles({ size }).input, InputProps?.classes?.input),
        },
      }}
      // InputLabelProps={{
      //   ...InputLabelProps,
      //   classes: { root: cx(inputLabelStyles().root, InputLabelProps?.classes?.root) },
      //   shrink: true,
      // }}
      FormHelperTextProps={{
        ...FormHelperTextProps,
        classes: { root: cx(formHelperTextStyles().root, FormHelperTextProps?.classes?.root) },
      }}
      {...materialTextFieldProps}
    />
  );
};

export { TextInput };
