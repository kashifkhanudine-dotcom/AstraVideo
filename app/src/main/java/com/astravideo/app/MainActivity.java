package com.astravideo.app;

import android.app.Activity;
import android.os.Bundle;
import android.graphics.Color;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;

public class MainActivity extends Activity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        int pad = (int) (20 * getResources().getDisplayMetrics().density);
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(pad, pad, pad, pad);
        root.setBackgroundColor(Color.rgb(248, 249, 252));

        TextView title = new TextView(this);
        title.setText("AstraVideo Studio");
        title.setTextSize(28);
        title.setTextColor(Color.BLACK);
        root.addView(title);

        TextView subtitle = new TextView(this);
        subtitle.setText("Planner video: 10 minuti = 60 scene da 10 secondi");
        subtitle.setTextSize(16);
        subtitle.setPadding(0, 8, 0, 20);
        root.addView(subtitle);

        EditText prompt = new EditText(this);
        prompt.setHint("Descrivi il video che vuoi creare...");
        prompt.setMinLines(4);
        prompt.setGravity(android.view.Gravity.TOP);
        root.addView(prompt, new LinearLayout.LayoutParams(-1, -2));

        Button generate = new Button(this);
        generate.setText("Crea piano da 60 scene");
        root.addView(generate);

        TextView output = new TextView(this);
        output.setTextSize(15);
        output.setPadding(0, 16, 0, 0);
        root.addView(output);

        generate.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                String p = prompt.getText().toString().trim();
                if (p.isEmpty()) {
                    output.setText("Inserisci prima un prompt.");
                    return;
                }
                StringBuilder sb = new StringBuilder();
                sb.append("Progetto creato\n\nPrompt: ").append(p).append("\n\n");
                for (int i = 1; i <= 60; i++) {
                    int start = (i - 1) * 10;
                    int end = i * 10;
                    sb.append("Scena ").append(i)
                      .append("  [").append(start).append("s–").append(end).append("s]\n");
                }
                output.setText(sb.toString());
            }
        });

        ScrollView scroll = new ScrollView(this);
        scroll.addView(root);
        setContentView(scroll);
    }
}
