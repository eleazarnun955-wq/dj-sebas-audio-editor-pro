package com.djsebas.audioeditor;

import android.app.Activity;
import android.content.ContentValues;
import android.database.Cursor;
import org.json.JSONArray;
import org.json.JSONObject;
import android.content.Intent;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.provider.MediaStore;
import android.webkit.JavascriptInterface;
import android.webkit.PermissionRequest;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.Manifest;
import android.content.pm.PackageManager;
import android.util.Base64;
import java.io.OutputStream;

public class MainActivity extends Activity {
  private static final int FILE_CHOOSER = 101;
  private static final int MIC_PERMISSION = 102;
  private ValueCallback<Uri[]> fileCallback;
  private PermissionRequest pendingPermission;
  private WebView web;

  public class ExportBridge {
    @JavascriptInterface
    public String saveMp3(String base64, String requestedName) {
      Uri savedUri = null;
      try {
        if (Build.VERSION.SDK_INT < 29) return "ERROR|Se requiere Android 10 o posterior para guardar en la carpeta de música.";
        String safeName = requestedName == null ? "DJ_SEBAS_AUDIO.mp3" : requestedName.replaceAll("[^a-zA-Z0-9._-]", "_");
        if (!safeName.toLowerCase().endsWith(".mp3")) safeName += ".mp3";
        byte[] bytes = Base64.decode(base64, Base64.DEFAULT);
        ContentValues values = new ContentValues();
        values.put(MediaStore.Audio.Media.DISPLAY_NAME, safeName);
        values.put(MediaStore.Audio.Media.MIME_TYPE, "audio/mpeg");
        values.put(MediaStore.Audio.Media.RELATIVE_PATH, "Music/DJ SEBAS AUDIO EDITOR PRO");
        values.put(MediaStore.Audio.Media.IS_PENDING, 1);
        savedUri = getContentResolver().insert(MediaStore.Audio.Media.EXTERNAL_CONTENT_URI, values);
        if (savedUri == null) return "ERROR|Android no pudo crear el archivo MP3.";
        try (OutputStream out = getContentResolver().openOutputStream(savedUri)) {
          if (out == null) throw new Exception("No se pudo abrir el archivo de destino");
          out.write(bytes);
          out.flush();
        }
        ContentValues ready = new ContentValues();
        ready.put(MediaStore.Audio.Media.IS_PENDING, 0);
        getContentResolver().update(savedUri, ready, null, null);
        return "OK|Music/DJ SEBAS AUDIO EDITOR PRO/" + safeName;
      } catch (Exception e) {
        if (savedUri != null) getContentResolver().delete(savedUri, null, null);
        String message = e.getMessage() == null ? "Error desconocido" : e.getMessage().replace("|", " ");
        return "ERROR|" + message;
      }
    }
    @JavascriptInterface
    public String listMp3() {
      JSONArray files = new JSONArray();
      if (Build.VERSION.SDK_INT < 29) return files.toString();
      String folder = "Music/DJ SEBAS AUDIO EDITOR PRO/";
      String[] projection = {
        MediaStore.Audio.Media.DISPLAY_NAME,
        MediaStore.Audio.Media.SIZE,
        MediaStore.Audio.Media.DATE_ADDED
      };
      try (Cursor cursor = getContentResolver().query(
          MediaStore.Audio.Media.EXTERNAL_CONTENT_URI,
          projection,
          MediaStore.MediaColumns.RELATIVE_PATH + " = ?",
          new String[]{folder},
          MediaStore.Audio.Media.DATE_ADDED + " DESC")) {
        if (cursor != null) {
          int nameCol = cursor.getColumnIndexOrThrow(MediaStore.Audio.Media.DISPLAY_NAME);
          int sizeCol = cursor.getColumnIndexOrThrow(MediaStore.Audio.Media.SIZE);
          int dateCol = cursor.getColumnIndexOrThrow(MediaStore.Audio.Media.DATE_ADDED);
          while (cursor.moveToNext()) {
            JSONObject item = new JSONObject();
            item.put("name", cursor.getString(nameCol));
            item.put("size", cursor.getLong(sizeCol));
            item.put("dateAdded", cursor.getLong(dateCol));
            files.put(item);
          }
        }
      } catch (Exception ignored) {
        return "[]";
      }
      return files.toString();
    }
  }



  @Override public void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    getWindow().setStatusBarColor(android.graphics.Color.rgb(8,2,15));
    web = new WebView(this);
    WebSettings s = web.getSettings();
    s.setJavaScriptEnabled(true);
    s.setDomStorageEnabled(true);
    s.setAllowFileAccess(true);
    s.setAllowContentAccess(true);
    s.setMediaPlaybackRequiresUserGesture(false);
    web.addJavascriptInterface(new ExportBridge(), "AndroidExport");
    web.setWebViewClient(new WebViewClient());
    web.setWebChromeClient(new WebChromeClient() {
      @Override public boolean onShowFileChooser(WebView view, ValueCallback<Uri[]> callback, FileChooserParams params) {
        if (fileCallback != null) fileCallback.onReceiveValue(null);
        fileCallback = callback;
        Intent intent = params.createIntent();
        try { startActivityForResult(intent, FILE_CHOOSER); }
        catch (Exception e) { fileCallback = null; return false; }
        return true;
      }
      @Override public void onPermissionRequest(PermissionRequest request) {
        runOnUiThread(() -> {
          if (Build.VERSION.SDK_INT >= 23 && checkSelfPermission(Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
            pendingPermission = request;
            requestPermissions(new String[]{Manifest.permission.RECORD_AUDIO}, MIC_PERMISSION);
          } else request.grant(request.getResources());
        });
      }
    });
    setContentView(web);
    web.loadUrl("file:///android_asset/index.html");
  }

  @Override protected void onActivityResult(int requestCode, int resultCode, Intent data) {
    super.onActivityResult(requestCode, resultCode, data);
    if (requestCode == FILE_CHOOSER && fileCallback != null) {
      Uri[] results = WebChromeClient.FileChooserParams.parseResult(resultCode, data);
      fileCallback.onReceiveValue(results);
      fileCallback = null;
    }
  }

  @Override public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
    super.onRequestPermissionsResult(requestCode, permissions, grantResults);
    if (requestCode == MIC_PERMISSION && pendingPermission != null) {
      if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED)
        pendingPermission.grant(pendingPermission.getResources());
      else pendingPermission.deny();
      pendingPermission = null;
    }
  }

  @Override public void onBackPressed() {
    if (web != null && web.canGoBack()) web.goBack(); else super.onBackPressed();
  }
}