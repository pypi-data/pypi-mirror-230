import React from 'react';
import { usePluginEnvironment } from '../../../utils/PluginEnvironmentProvider';
import { StudioJobEnvironment } from '../Studio/StudioJobEnvironment';
import { DefaultJobEnvironment } from './DefaultJobEnvironment';
import { JobEnvironmentProps } from './jobEnvironment';

export const JobEnvironmentContainer: React.FC<JobEnvironmentProps> = (props) => {
  const { pluginEnvironment } = usePluginEnvironment();

  return (<>
    {pluginEnvironment.isStudio && (
      <StudioJobEnvironment
        {...props}
      ></StudioJobEnvironment>
    )}

    {pluginEnvironment.isLocalJL && (
      <DefaultJobEnvironment
        {...props}
      ></DefaultJobEnvironment>
    )}
  </>);
}
