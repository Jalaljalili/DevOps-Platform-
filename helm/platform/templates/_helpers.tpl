{{- define "platform.name" -}}platform{{- end -}}
{{- define "platform.fullname" -}}{{- printf "%s" .Release.Name -}}{{- end -}}
