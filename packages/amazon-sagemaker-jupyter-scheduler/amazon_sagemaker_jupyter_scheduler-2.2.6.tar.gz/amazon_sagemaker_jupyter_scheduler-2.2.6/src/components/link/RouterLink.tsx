import React from 'react';
import MuiLink, { LinkProps as MuiLinkProps } from '@material-ui/core/Link';
import { cx } from '@emotion/css';
import { LinkUnderline } from './types';
import { LinkBase } from './styles';
import { Link as RouterLinkInt } from 'react-router-dom';

export interface RouterLinkProps extends MuiLinkProps {
  readonly disabled?: boolean;
  readonly underline?: LinkUnderline;
  readonly to?: string;
}

const RouterLink: React.FunctionComponent<RouterLinkProps> = ({ className, children, to, ...materialLinkProps }) => {
  const props = {
    ...materialLinkProps,
    className: cx(LinkBase(), className),
    to,
    component: RouterLinkInt,
  };

  return <MuiLink {...props}>{children}</MuiLink>;
};

export { RouterLink };
