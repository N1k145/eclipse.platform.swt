/*******************************************************************************
 * Copyright (c) 2026 Aleksandar Kurtakov and others.
 *
 * This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License 2.0
 * which accompanies this distribution, and is available at
 * https://www.eclipse.org/legal/epl-2.0/
 *
 * SPDX-License-Identifier: EPL-2.0
 *
 * Contributors:
 *     Aleksandar Kurtakov - initial API and implementation
 *******************************************************************************/
package org.eclipse.swt.tests.gtk;

import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assumptions.assumeTrue;

import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;

import org.eclipse.swt.widgets.Display;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

public class Test_GtkDevice {

	/**
	 * Loads data/font/swt-test-font.ttf, see data/font/README.md for how it is
	 * generated, and checks that Pango then lists its family. A loaded font
	 * cannot be unloaded, so the test is skipped when the family is already
	 * listed, e.g. when AllGTKTests runs it a second time in the same process.
	 */
	@Test
	public void test_loadFont(@TempDir Path tempFolder) throws IOException {
		String family = "SWT Test Font";
		Path font = tempFolder.resolve("swt-test-font.ttf");
		try (InputStream in = Test_GtkDevice.class.getResourceAsStream("/font/swt-test-font.ttf")) {
			assertNotNull(in, "font resource not found");
			Files.copy(in, font);
		}
		Display display = Display.getDefault();
		assumeTrue(display.getFontList(family, true).length == 0, "the test font is already installed or loaded");
		assertTrue(display.loadFont(font.toString()));
		assertTrue(display.getFontList(family, true).length > 0, "the loaded font is not listed");
	}
}
