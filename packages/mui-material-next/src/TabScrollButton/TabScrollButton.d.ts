import * as React from 'react';
import { SxProps } from '@mui/system';
import { InternalStandardProps as StandardProps, Theme } from '@mui/material';
import { TabScrollButtonClasses } from './tabScrollButtonClasses';

export interface TabScrollButtonProps extends StandardProps<React.HTMLAttributes<HTMLDivElement>> {
  /**
   * The content of the component.
   */
  children?: React.ReactNode;
  /**
   * Override or extend the styles applied to the component.
   */
  classes?: Partial<TabScrollButtonClasses>;
  /**
   * The components used for each slot inside.
   *
   * This prop is an alias for the `slots` prop.
   * It's recommended to use the `slots` prop instead.
   *
   * @default {}
   */
  components?: {
    leftIcon?: React.ElementType;
    rightIcon?: React.ElementType;
  };
  /**
   * The direction the button should indicate.
   */
  direction: 'left' | 'right';
  /**
   * If `true`, the component is disabled.
   */
  disabled?: boolean;
  /**
   * The component orientation (layout flow direction).
   */
  orientation: 'horizontal' | 'vertical';
  /**
   * The components used for each slot inside.
   *
   * This prop is an alias for the `components` prop, which will be deprecated in the future.
   *
   * @default {}
   */
  slots?: {
    leftIcon?: React.ElementType;
    rightIcon?: React.ElementType;
  };
  /**
   * The system prop that allows defining system overrides as well as additional CSS styles.
   */
  sx?: SxProps<Theme>;
}

/**
 *
 * Demos:
 *
 * - [Tabs](https://mui.com/components/tabs/)
 *
 * API:
 *
 * - [TabScrollButton API](https://mui.com/api/tab-scroll-button/)
 */
export default function TabScrollButton(props: TabScrollButtonProps): JSX.Element;
