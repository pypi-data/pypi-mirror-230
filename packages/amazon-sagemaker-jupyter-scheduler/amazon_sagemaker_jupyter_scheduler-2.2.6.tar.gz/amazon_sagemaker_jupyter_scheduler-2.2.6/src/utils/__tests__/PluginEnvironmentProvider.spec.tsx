import { JupyterFrontEnd } from '@jupyterlab/application';
import { ReactWrapper, mount } from 'enzyme';
import React from 'react';
import { PluginEnvironment, PluginEnvironmentProvider, PluginEnvironmentType, STUDIO_SAGEMAKER_UI_PLUGIN_ID, usePluginEnvironment } from '../PluginEnvironmentProvider';

let mockApp: JupyterFrontEnd;
let pluginEnvironment: PluginEnvironment;

const PluginEnvironmentProviderTester = () => {
  const instance = usePluginEnvironment();
  pluginEnvironment = instance.pluginEnvironment;
  return <>{pluginEnvironment.type}</>;
};

function mountProvider(): ReactWrapper {
  return mount(<PluginEnvironmentProvider app={mockApp}>
    <PluginEnvironmentProviderTester />
  </PluginEnvironmentProvider>);
}

describe('PluginEnvironmentProvider', () => {
  beforeEach(() => {
    mockApp = {
      hasPlugin: jest.fn().mockReturnValue(false),
    } as unknown as JupyterFrontEnd;
  });

  it('initializes correctly with LocalJL plugin environment', () => {
    const wrapper = mountProvider();

    expect(wrapper.findWhere(node => node.contains(PluginEnvironmentType.LocalJL))).toBeDefined();
    expect(pluginEnvironment).toBeDefined();
    expect(pluginEnvironment.type).toEqual(PluginEnvironmentType.LocalJL);
    expect(pluginEnvironment.isStudio).toBeFalsy();
    expect(pluginEnvironment.isLocalJL).toBeTruthy();
  });

  it('initializes correctly with Studio plugin environment', () => {
    mockApp.hasPlugin = (plugin: string) => plugin === STUDIO_SAGEMAKER_UI_PLUGIN_ID;
    const wrapper = mountProvider();

    expect(wrapper.findWhere(node => node.contains(PluginEnvironmentType.Studio))).toBeDefined();
    expect(pluginEnvironment.type).toEqual(PluginEnvironmentType.Studio);
    expect(pluginEnvironment.isStudio).toBeTruthy();
    expect(pluginEnvironment.isLocalJL).toBeFalsy();
  });
});
